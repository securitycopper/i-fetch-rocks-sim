from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


WIRE_LABELS = {
    5: ("data", "build_network_in", "build_network_out"),
    4: ("large data", "build_large_network_in", "build_large_network_out"),
    2: ("power", "build_power_network_in", "build_power_out"),
    3: ("power", "build_power_network_in", "build_power_out"),
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

INPUT_BUILDERS = [
    ("network_in_data", "build_network_in"),
    ("large_network_in_data", "build_large_network_in"),
    ("power_in_data", "build_power_network_in"),
    ("large_power_in_data", "build_power_network_in"),
]

OUTPUT_BUILDERS = [
    ("network_out_data", "build_network_out"),
    ("large_network_out_data", "build_large_network_out"),
    ("power_out_data", "build_power_out"),
    ("large_power_out_data", "build_large_power_out"),
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _simulator_path() -> Path:
    return _repo_root() / "code" / "ifetchrocks" / "sim" / "simulator.py"


def _internal_componenttype_path() -> Path:
    return _repo_root() / "code" / "ifetchrocks" / "cpu" / "programmer" / "_internal" / "componenttype.py"


def _normalize(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def _tokenize(text: str) -> List[str]:
    tokens: List[str] = []
    current: List[str] = []
    for ch in text:
        if ch.isalnum():
            current.append(ch.lower())
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))

    expanded: List[str] = []
    for token in tokens:
        if token:
            expanded.append(token)
    if expanded:
        return expanded
    return [text.lower()] if text else []


def _extract_string(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _extract_string(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_int(node: ast.AST) -> Optional[int]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _load_enum_mapping(path: Path, enum_name: str) -> Dict[str, object]:
    if not path.exists():
        return {}
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == enum_name:
            mapping: Dict[str, object] = {}
            for stmt in item.body:
                if not isinstance(stmt, ast.Assign):
                    continue
                if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                    continue
                key = stmt.targets[0].id
                int_value = _extract_int(stmt.value)
                if int_value is not None:
                    mapping[key] = int_value
                    continue
                string_value = _extract_string(stmt.value)
                if string_value is not None:
                    mapping[key] = string_value
            return mapping
    return {}


def _load_type_name_lookup() -> Dict[int, str]:
    lookup: Dict[int, str] = {}
    simulator_mapping = _load_enum_mapping(_simulator_path(), "ComponentType")
    for name, value in simulator_mapping.items():
        if isinstance(value, int):
            lookup[value] = name

    internal_mapping = _load_enum_mapping(_internal_componenttype_path(), "ComponentType")
    for name, value in internal_mapping.items():
        if isinstance(value, int) and value not in lookup:
            lookup[value] = name
    return lookup


def _load_device_class_lookup() -> Dict[str, str]:
    simulator_mapping = _load_enum_mapping(_simulator_path(), "DeviceClasses")
    return {name: str(value) for name, value in simulator_mapping.items() if isinstance(value, str)}


TYPE_NAME_LOOKUP = _load_type_name_lookup()
DEVICE_CLASS_LOOKUP = _load_device_class_lookup()


def find_all_components(save_path: Path) -> List[dict]:
    try:
        payload = json.loads(save_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    components: List[dict] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if {"type", "uuid", "indexedChildren"}.issubset(node.keys()):
                components.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(payload)
    return components


def scan_all_saves(saves_dir: Path | str) -> List[dict]:
    saves_path = Path(saves_dir)
    components: List[dict] = []
    for save_path in sorted(saves_path.rglob("*.json")):
        if save_path.name.endswith(".meta"):
            continue
        components.extend(find_all_components(save_path))
    return components


def get_component_example(type_id: int, saves_dir: Path | str) -> Optional[dict]:
    for component in scan_all_saves(saves_dir):
        if component.get("type") == type_id:
            return component
    return None


def _is_manual_candidate(type_name: str, filename_stem: str) -> bool:
    if not type_name:
        return False
    normalized_type = _normalize(type_name)
    normalized_stem = _normalize(filename_stem)
    if not normalized_type or not normalized_stem:
        return False
    if normalized_type in normalized_stem or normalized_stem in normalized_type:
        return True

    type_tokens = set(_tokenize(type_name))
    stem_tokens = set(_tokenize(filename_stem))
    if not type_tokens or not stem_tokens:
        return False
    return len(type_tokens & stem_tokens) >= 2


def find_manual_page(type_name: str, manual_dir: Path | str) -> Optional[Tuple[str, str, str]]:
    manual_path = Path(manual_dir).resolve()
    candidates = sorted(manual_path.rglob("*.md"))
    if not candidates:
        return None

    best_path: Optional[Path] = None
    best_score = 0
    type_tokens = set(_tokenize(type_name))
    normalized_type = _normalize(type_name)

    for candidate in candidates:
        stem = candidate.stem
        normalized_stem = _normalize(stem)
        score = 0
        if normalized_type and normalized_type in normalized_stem:
            score = 1000 + len(normalized_type)
        elif normalized_stem and normalized_stem in normalized_type:
            score = 900 + len(normalized_stem)
        else:
            stem_tokens = set(_tokenize(stem))
            overlap = len(type_tokens & stem_tokens)
            if overlap:
                score = overlap * 100
                if _is_manual_candidate(type_name, stem):
                    score += 50

        if score > best_score:
            best_score = score
            best_path = candidate

    if best_path is None or best_score <= 0:
        return None

    heading = ""
    image_line = ""
    for line in best_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not heading and stripped.startswith("# "):
            heading = stripped
        elif not image_line and stripped.startswith("![]("):
            image_line = stripped
        if heading and image_line:
            break

    if not heading:
        heading = f"# {type_name}"
    if not image_line:
        image_line = "![](images/unknown.png)"

    relative_path = best_path.resolve().relative_to(_repo_root()).as_posix()
    return relative_path, heading, image_line


def _image_url_from_manual_line(image_line: str) -> str:
    start = image_line.find("(")
    end = image_line.rfind(")")
    if start == -1 or end == -1 or end <= start + 1:
        return ""
    image_rel = image_line[start + 1 : end].strip()
    image_name = Path(image_rel).name
    return f"http://ifetch.rocks/manual/images/{image_name}"


def _component_type_name(type_id: int) -> str:
    return TYPE_NAME_LOOKUP.get(type_id, "unknown")


def _component_class_name(type_id: int) -> str:
    type_name = _component_type_name(type_id)
    return DEVICE_CLASS_LOOKUP.get(type_name, f"Device{type_id}")


def _connection_groups(component: dict) -> Tuple[List[Tuple[str, str]], Dict[str, List[str]], Dict[str, List[str]]]:
    comments: List[Tuple[str, str]] = []
    inputs: Dict[str, List[str]] = {"network_in_data": [], "large_network_in_data": [], "power_in_data": [], "large_power_in_data": []}
    outputs: Dict[str, List[str]] = {"network_out_data": [], "large_network_out_data": [], "power_out_data": [], "large_power_out_data": []}

    indexed_children = component.get("indexedChildren", {})
    for connection_id, child in indexed_children.items():
        if not isinstance(child, dict):
            continue
        connection_type = child.get("type")
        if connection_id is None:
            continue
        label, input_builder, output_builder = WIRE_LABELS.get(connection_type, (f"type {connection_type}", "build_network_in", "build_network_out"))
        comments.append((str(connection_id), label))
        if connection_type == 5:
            inputs["network_in_data"].append(str(connection_id))
        elif connection_type == 4:
            inputs["large_network_in_data"].append(str(connection_id))
        elif connection_type in (2, 3):
            inputs["power_in_data"].append(str(connection_id))
        else:
            inputs["network_in_data"].append(str(connection_id))

    return comments, inputs, outputs


def _format_description_mapping(connection_ids: Sequence[str]) -> str:
    if not connection_ids:
        return "{}"
    lines = ["{"]
    for index, connection_id in enumerate(connection_ids):
        label = f"TODO_{index + 1}"
        comment = "# data wire"
        lines.append(f"            {connection_id!r}: {label!r},   {comment}")
    lines.append("        }")
    return "\n".join(lines)


def _format_empty_mapping() -> str:
    return "{\n        }"


def _render_stub(type_id: int, type_name: str, class_name: str, manual_info: Optional[Tuple[str, str, str]], component: Optional[dict]) -> str:
    manual_path = manual_info[0] if manual_info else "(not found)"
    heading = manual_info[1] if manual_info else f"# {type_name}"
    image_line = manual_info[2] if manual_info else "![](images/unknown.png)"
    image_url = _image_url_from_manual_line(image_line)

    comments, inputs, _ = _connection_groups(component or {})
    device_data = sorted((component or {}).get("indexedDeviceData", {}).keys()) if isinstance((component or {}).get("indexedDeviceData", {}), dict) else []

    input_comments = [f"#   {connection_id} ({label})" for connection_id, label in comments]
    if not input_comments:
        input_comments = ["#   (none)"]

    device_data_lines = ["# Device data keys (indexedDeviceData):"]
    if device_data:
        for key in device_data:
            device_data_lines.append(f"#   {key}")
    else:
        device_data_lines[0] += " (none)"

    type_name_display = type_name if type_name != "unknown" else f"type {type_id}"
    lines: List[str] = []
    lines.append(f"# STUB generated by stub_generator.py — type {type_id} ({type_name_display})")
    lines.append(f"# Manual: {manual_path}")
    if comments:
        lines.append("# TODO: move output connections from build_network_in → build_network_out")
    lines.append(f"# TODO: implement change_event logic (see {manual_path})")
    lines.append("# Connection IDs found in save (all listed as inputs — mark outputs manually):")
    lines.extend(input_comments)
    lines.extend(device_data_lines)
    lines.append("")
    lines.append("from ifetchrocks_sim.network.data_network_manager import DataNetworkManager")
    lines.append("from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \\")
    lines.append("    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, \\")
    lines.append("    build_large_power_out, graph_mappings, register_listeners")
    lines.append("")
    lines.append("")
    lines.append(f"class {class_name}:")
    lines.append(f"    \"\"\"{type_name.upper() if type_name != 'unknown' else 'unknown'} — {heading[2:] if heading.startswith('# ') else heading}")
    lines.append(f"    Manual: {manual_path}")
    lines.append("    \"\"\"")
    lines.append("")
    lines.append("    def __init__(self, network_manager: DataNetworkManager, data: dict):")
    lines.append("        self.data = data")
    lines.append("        self.network_manager = network_manager")
    lines.append("        self.uuid = data['uuid']")
    lines.append(f"        self.type = {type_id}")
    lines.append(f"        self.name = {class_name!r}")
    lines.append(f"        self.image = {image_url!r}")
    lines.append("        self.value = data['signalValue']")
    lines.append("")
    lines.append("        # ----- Inputs (TODO: move outputs to build_network_out below) -----")
    lines.append("        self.network_in_data = build_network_in(")
    lines.append("            network_manager=network_manager, data=data, change_event=self.change_event,")
    lines.append("            network_in_descriptions={")
    for connection_id in inputs["network_in_data"]:
        lines.append(f"                {connection_id!r}: 'TODO',   # data wire")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.large_network_in_data = build_large_network_in(")
    lines.append("            network_manager=network_manager, data=data, change_event=self.change_event,")
    lines.append("            network_in_descriptions={")
    for connection_id in inputs["large_network_in_data"]:
        lines.append(f"                {connection_id!r}: 'TODO',   # large data wire")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.power_in_data = build_power_network_in(")
    lines.append("            network_manager=network_manager, data=data, change_event=self.change_event,")
    lines.append("            network_in_descriptions={")
    for connection_id in inputs["power_in_data"]:
        lines.append(f"                {connection_id!r}: 'TODO',   # power wire")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.large_power_in_data = build_power_network_in(")
    lines.append("            network_manager=network_manager, data=data, change_event=self.change_event,")
    lines.append("            network_in_descriptions={")
    for connection_id in inputs["large_power_in_data"]:
        lines.append(f"                {connection_id!r}: 'TODO',   # power wire")
    lines.append("            }")
    lines.append("        )")
    lines.append("")
    lines.append("        # ----- Outputs (move connection IDs here once identified) -----")
    lines.append("        self.network_out_data = build_network_out(")
    lines.append("            network_manager=network_manager, data=data,")
    lines.append("            network_in_descriptions={")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.large_network_out_data = build_large_network_out(")
    lines.append("            network_manager=network_manager, data=data,")
    lines.append("            network_in_descriptions={")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.power_out_data = build_power_out(")
    lines.append("            network_manager=network_manager, data=data,")
    lines.append("            network_in_descriptions={")
    lines.append("            }")
    lines.append("        )")
    lines.append("        self.large_power_out_data = build_large_power_out(")
    lines.append("            network_manager=network_manager, data=data,")
    lines.append("            network_in_descriptions={")
    lines.append("            }")
    lines.append("        )")
    lines.append("")
    lines.append("        register_listeners(")
    lines.append("            network_manager=network_manager,")
    lines.append("            network_in_data=self.network_in_data,")
    lines.append("            large_network_in_data=self.large_network_in_data,")
    lines.append("            power_in_data=self.power_in_data,")
    lines.append("            large_power_in_data=self.large_power_in_data,")
    lines.append("        )")
    lines.append("        graph_mappings(self)")
    lines.append("")
    lines.append("    def change_event(self, component_id: str, value: int):")
    lines.append(f"        # TODO: implement logic — see {manual_path}")
    lines.append("        pass")
    lines.append("")
    return "\n".join(lines)


def generate_stub(type_id: int, saves_dir: Path | str, manual_dir: Path | str) -> str:
    type_name = _component_type_name(type_id)
    class_name = _component_class_name(type_id)
    manual_info = find_manual_page(type_name, manual_dir) if type_name != "unknown" else None
    component = get_component_example(type_id, saves_dir)
    return _render_stub(type_id, type_name, class_name, manual_info, component)


def gaps_report(saves_dir: Path | str, manual_dir: Path | str) -> str:
    components = scan_all_saves(saves_dir)
    counts = Counter(component.get("type") for component in components if isinstance(component.get("type"), int))
    implemented_type_names = set(DEVICE_CLASS_LOOKUP.keys())

    rows: List[Tuple[int, int, str, str]] = []
    for type_id, count in counts.items():
        type_name = _component_type_name(type_id)
        if type_name in implemented_type_names:
            continue
        manual_info = find_manual_page(type_name, manual_dir) if type_name != "unknown" else None
        if manual_info:
            manual_text = Path(manual_info[0]).name
        else:
            manual_text = "(not found)"
        rows.append((count, type_id, type_name, manual_text))

    rows.sort(key=lambda item: (-item[0], item[1]))
    lines = ["Unimplemented type IDs found in save files:"]
    if not rows:
        lines.append("  (none)")
        return "\n".join(lines)

    for count, type_id, type_name, manual_text in rows:
        lines.append(
            f"  type {type_id:>3}  (count: {count:>2}) — ComponentType name: {type_name:<24} manual: {manual_text}"
        )
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate device stubs from save files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--type", type=int, help="Generate a stub for a single component type id.")
    group.add_argument("--gaps", action="store_true", help="List unimplemented types found in save files.")
    parser.add_argument("--saves", default="game_app_data/Saves", help="Path to the save folder.")
    parser.add_argument("--manual", default="docs/manual", help="Path to the manual folder.")
    args = parser.parse_args(argv)

    if args.type is not None:
        print(generate_stub(args.type, args.saves, args.manual))
        return 0

    if args.gaps:
        print(gaps_report(args.saves, args.manual))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
