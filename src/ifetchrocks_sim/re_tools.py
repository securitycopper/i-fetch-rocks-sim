"""Reverse-engineering API for device port identification.

Consolidates the ad-hoc scripts (_rm_find_new2.py, port_dump_re2.py, etc.)
into importable, tested functions that the DeviceRE agent can call directly
instead of creating temp Python files each session.

Typical one-liner usage from a terminal or agent::

    from ifetchrocks_sim.re_tools import RESave
    re = RESave()                       # loads fixed RE save
    re.print_new_devices()              # diff against baseline
    re.print_port_map(type_id=214)      # port dump with probe annotations

Full workflow::

    re = RESave()
    new = re.find_new_devices()         # -> list[NewDeviceInfo]
    ports = re.port_map(type_id=214)    # -> list[PortInfo]
    re.print_port_map(type_id=214)      # pretty-printed table
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RE_SAVE_PATH = (
    Path(__file__).resolve().parents[3]
    / 'game_app_data' / 'Saves'
    / '102d6094-bff6-413a-b859-b4992647c9e5.json'
)

# Probe wire table — wire UUIDs from the RE save's indexedChildren.
# Populated 2026-03-23 (IN/VD), extended 2026-03-26 (VM/VS).
PROBE_WIRES: Dict[str, Dict[str, Any]] = {
    # Single-channel inputs (FourBitSwitch)
    '707e5155-7809-4fde-9e4c-8e14fd220167': {'name': 'IN_0',  'kind': 'input', 'value': 0},
    '5ddfa3b9-094d-4526-a4b6-fa51de0b2064': {'name': 'IN_1',  'kind': 'input', 'value': 1},
    '1ff01b1d-02f2-409f-86ad-29df09d9feb5': {'name': 'IN_2',  'kind': 'input', 'value': 2},
    'b8345e88-40c3-4c36-b50d-cbac88f81792': {'name': 'IN_3',  'kind': 'input', 'value': 3},
    'c3c32224-2e63-45f9-b106-10c2ad43abf2': {'name': 'IN_4',  'kind': 'input', 'value': 4},
    '35d33283-f128-482b-a4b0-966d3097d473': {'name': 'IN_5',  'kind': 'input', 'value': 5},
    '8c106dd0-e99b-4350-bb22-25724b164dac': {'name': 'IN_6',  'kind': 'input', 'value': 6},
    '0940f665-591a-479c-9a97-1091f2b8db92': {'name': 'IN_7',  'kind': 'input', 'value': 7},
    '24e2b0bc-d366-4d9e-b7a1-87d4901c4734': {'name': 'IN_8',  'kind': 'input', 'value': 8},
    '95ebc1e1-27e3-4450-8551-7df2d1f010c9': {'name': 'IN_9',  'kind': 'input', 'value': 9},
    'de12c063-8383-4870-a49f-e12d0bed49a1': {'name': 'IN_10', 'kind': 'input', 'value': 10},
    '6c938282-3404-44ed-aa16-6e53d9ab1cc7': {'name': 'IN_11', 'kind': 'input', 'value': 11},
    '25a45a72-d5b8-4052-8d3f-66953c50bdae': {'name': 'IN_12', 'kind': 'input', 'value': 12},
    '760e4982-72fc-4d9b-854e-f2f913ad2e5b': {'name': 'IN_13', 'kind': 'input', 'value': 13},
    '462d7917-54fd-4c61-a30b-e3a022f2f45f': {'name': 'IN_14', 'kind': 'input', 'value': 14},
    'af84c50f-5397-47aa-a712-5516ae1abc64': {'name': 'IN_15', 'kind': 'input', 'value': 15},
    '5aecf3d5-c126-4339-ac93-489b2eea41a7': {'name': 'IN_MAX', 'kind': 'input', 'value': 65535},

    # Single-channel outputs (ValueDisplay)
    '034efbe8-e971-419a-bfe0-26a5c05184b6': {'name': 'VD_0',  'kind': 'output'},
    'c1351328-a2b8-4e8b-ba52-196bfded2f52': {'name': 'VD_1',  'kind': 'output'},
    '65c07caa-4fd6-40ec-aa04-e56ba54d28d0': {'name': 'VD_2',  'kind': 'output'},
    'ff11fd94-34c5-45c2-9cc9-0c85ccedcb0f': {'name': 'VD_3',  'kind': 'output'},
    'b888dc5d-434a-4dd0-a71d-f0fc11f37c48': {'name': 'VD_4',  'kind': 'output'},
    '04440798-98b4-40d1-8176-7ac981bbf814': {'name': 'VD_5',  'kind': 'output'},
    'c909cbbf-19df-4313-b80d-387d3ee94086': {'name': 'VD_6',  'kind': 'output'},
    'f2a5662b-c928-4560-a922-ed455ebd3902': {'name': 'VD_7',  'kind': 'output'},
    '064eac82-b723-4799-8cd3-b8fd7f0f302a': {'name': 'VD_8',  'kind': 'output'},
    '67c8b28e-4600-4abb-97a4-677ede5889ac': {'name': 'VD_9',  'kind': 'output'},
    '600978da-2a5d-43f7-8400-2883abd9f5f7': {'name': 'VD_10', 'kind': 'output'},
    'a13d62eb-3d9f-4491-a001-4ccd70925616': {'name': 'VD_11', 'kind': 'output'},
    '1a35f8d2-6464-43fc-9b01-a4a5daff05d9': {'name': 'VD_12', 'kind': 'output'},
    'eab85d2b-44f8-4a4c-a643-6807cb12f739': {'name': 'VD_13', 'kind': 'output'},
    '00f537ce-a909-43aa-a6e4-1e90fb866290': {'name': 'VD_14', 'kind': 'output'},
    'ae688c1f-9d17-49f4-bf53-e49de04eb90f': {'name': 'VD_15', 'kind': 'output'},

    # Vector probes (PacketVectorMerger / Splitter)
    '701e37ef-fc47-46fe-bdea-7aa650734196': {'name': 'VM_1',  'kind': 'vector_input'},
    'eb5fc108-ea27-4163-bca7-b2b0e3d7a1c0': {'name': 'VM_2',  'kind': 'vector_input'},
    '42b16eeb-37f7-4226-945d-755983c2c5bd': {'name': 'VM_3',  'kind': 'vector_input'},
    '01cdfac9-aeda-49d2-8c3a-07f72ebcf81c': {'name': 'VM_4',  'kind': 'vector_input'},
    'f5776785-c787-4811-9f1c-601c830d84a6': {'name': 'VMO',   'kind': 'large_output'},
    'e4573826-96ff-4c45-ae60-d26915a35eb9': {'name': 'VSI',   'kind': 'large_input'},
    'a422b1da-09a9-415c-8350-3747d530ee95': {'name': 'VS_1',  'kind': 'vector_output'},
    'e67959a8-38a7-463b-8178-9e3242a85553': {'name': 'VS_2',  'kind': 'vector_output'},
    '027bf5d4-8078-47ae-ab5c-b18b58883aa9': {'name': 'VS_3',  'kind': 'vector_output'},
    '91e38ef2-d618-473e-9928-c0ffeba3599b': {'name': 'VS_4',  'kind': 'vector_output'},
}

# Child type to network kind mapping
_CHILD_TYPE_NAMES: Dict[int, str] = {
    2: 'LargePowerWire',
    3: 'PowerWire',
    4: 'LargeNetwork',
    5: 'Network',
    139: 'MemoryBay',
    142: 'VectorCable',
    156: 'DriveSlot',
    157: 'DriveSlot',
}

# Connection kinds for room-to-room cable endpoints.
# Maps child_type (as seen in indexedChildren) to a human-readable kind name.
CONNECTION_KINDS: Dict[int, str] = {
    2: 'large_power',
    3: 'small_power',
    4: 'large_data',
    5: 'small_data',
    142: 'vector',
}

# Baseline UUID set from the RE save (2026-03-26, full probe infrastructure).
# Any UUID found in the RE save that is NOT in this set is a newly placed device.
BASELINE_UUIDS: Set[str] = {
    '1ec5c991-50a9-4203-b478-309ebfed0a09', '3a10ba9e-c89d-4d8d-b44c-d56151d6dfef',
    '5ec0da90-955c-4c50-b24b-ba283c703422', '73329139-d02e-46a2-b1cb-1aa508d25b8c',
    'c33bced5-78e4-4901-9666-c55b353b8831', 'dc0fea90-f477-4db1-b21d-294dd9bc0ce4',
    '2fea4c2b-df0e-4639-b221-17f36850f565', '4cb2bf41-6416-48ec-8a03-5af14fa8daa4',
    '535578c1-0dda-40c3-b96b-e8ecd0bef914', '6b2152f9-51f2-4000-bf5b-89d63592db33',
    '9007b03a-e4b1-4b15-8024-6d0d1175b1a7', 'c7b18263-2138-483d-bdbb-4ae97db7e212',
    'cfa93768-72e6-4516-bed9-81377608630f', 'c043bcae-3195-4982-b9db-c5d02c066107',
    '238824ec-dad4-4074-acac-2cc0303f60af', '5f181b31-8063-4165-92fc-f8fb1a9990e0',
    '035f1656-0111-4ab4-a4ac-e0115edbe66f', '922d51e3-9e02-49b7-9a48-28596385ff7d',
    'ba2dc787-ed16-4660-b66f-e6c4744d76f6', 'd8d1b61f-776e-4b8f-a5cf-d98902fd6446',
    '9e353b64-9eb6-4e33-b654-d67155b6139e', 'a8c3da7c-7d48-4356-84d9-db470bf8b58c',
    '2d905b97-f826-42ff-81c4-212e57a588b0', '299693af-57ff-4167-be19-d840b28ce8e1',
    'cdfda64a-a66b-4a0c-a766-a6a6732a82ee', '79444fa9-fc47-4a48-af92-c2c3a8c44080',
    'cddf667a-4b4c-4d3d-929e-81ad966353c1', '2cecda0e-e1ce-4f07-8f76-7cfbc4284f65',
    '0412d59a-82b3-416b-b655-52f6ecba0155', 'af76f59e-e372-408d-a1c5-c8e7c4e112e2',
    '434b4c28-1127-4981-9472-386200c1f4b7', 'acdb2192-0295-4ff9-96c4-d0c2489a77da',
    'd54b4b00-9159-4f37-a52b-1dff638d24cc',
    'f5776785-c787-4811-9f1c-601c830d84a6', 'e4573826-96ff-4c45-ae60-d26915a35eb9',
    '707e5155-7809-4fde-9e4c-8e14fd220167',
    '034efbe8-e971-419a-bfe0-26a5c05184b6', 'c1351328-a2b8-4e8b-ba52-196bfded2f52',
    '65c07caa-4fd6-40ec-aa04-e56ba54d28d0', 'ff11fd94-34c5-45c2-9cc9-0c85ccedcb0f',
    'b888dc5d-434a-4dd0-a71d-f0fc11f37c48', '04440798-98b4-40d1-8176-7ac981bbf814',
    'c909cbbf-19df-4313-b80d-387d3ee94086', 'f2a5662b-c928-4560-a922-ed455ebd3902',
    '064eac82-b723-4799-8cd3-b8fd7f0f302a', '67c8b28e-4600-4abb-97a4-677ede5889ac',
    '600978da-2a5d-43f7-8400-2883abd9f5f7', 'a13d62eb-3d9f-4491-a001-4ccd70925616',
    '1a35f8d2-6464-43fc-9b01-a4a5daff05d9', 'eab85d2b-44f8-4a4c-a643-6807cb12f739',
    '00f537ce-a909-43aa-a6e4-1e90fb866290', 'ae688c1f-9d17-49f4-bf53-e49de04eb90f',
    '25a45a72-d5b8-4052-8d3f-66953c50bdae', '760e4982-72fc-4d9b-854e-f2f913ad2e5b',
    'c3c32224-2e63-45f9-b106-10c2ad43abf2', '35d33283-f128-482b-a4b0-966d3097d473',
    '8c106dd0-e99b-4350-bb22-25724b164dac', '0940f665-591a-479c-9a97-1091f2b8db92',
    '24e2b0bc-d366-4d9e-b7a1-87d4901c4734', '95ebc1e1-27e3-4450-8551-7df2d1f010c9',
    '5ddfa3b9-094d-4526-a4b6-fa51de0b2064', 'de12c063-8383-4870-a49f-e12d0bed49a1',
    '6c938282-3404-44ed-aa16-6e53d9ab1cc7', '1ff01b1d-02f2-409f-86ad-29df09d9feb5',
    'b8345e88-40c3-4c36-b50d-cbac88f81792', '462d7917-54fd-4c61-a30b-e3a022f2f45f',
    'af84c50f-5397-47aa-a712-5516ae1abc64', '5aecf3d5-c126-4339-ac93-489b2eea41a7',
    '7487c2d7-78dc-44f2-a790-22a0d9e088d9', '6e3c3755-2aab-47ef-8138-c4008e135941',
    '6642ebfe-07fa-4a63-adb5-affb369fa41b', '7453b2b4-d7be-4ab9-a583-2a126feff4b8',
    '95d3ca1c-3bf0-4cfb-98ee-dc9c4cc1c9df', 'a7febf6d-2182-4da1-82fe-ea8d7a48f6cd',
    '74c28dcd-0799-42d3-8142-511c40b26e75', 'd5ca7895-5231-496d-8c07-0bdceadbb69f',
    '17cfb76f-20df-443e-9a3e-55f06db01d43', '336c032a-119e-435a-beab-c36f7a54bc48',
    'f7ba5b07-d42f-45b9-a351-fb27bcc4bdb2', 'b8af1c42-9caa-450f-86d1-69fb7b7f1d16',
    'e43b1f07-dcd1-469a-a280-70081bd0fec9', 'a9b2728a-1083-41bf-b17a-52f6e86d8f7f',
    '4a6b5a26-89b2-4d32-b3f0-05e1e0c89e99', '7046cb76-245e-4aba-b03a-3477d75f175c',
    '590a6bd8-c146-4ea3-9c47-4d687eadf7e4', '9f70e815-49a0-476f-b748-52a763299cd2',
    '0605bc63-1079-4273-b22c-4ba07ff642f7', '4abb7970-c6f6-4f8a-a60b-84ce162a0d2e',
    '77c8fe06-6dee-4466-a2bd-122a6ce82aa3', '9d5138bc-ce98-4b0e-99f9-dd5fd5d8a3c9',
    '919685d6-511a-4b46-be14-221a5a470c20', '27decd09-89c6-4c82-a581-0d04ffe0067a',
    '0ebd9eab-80a6-4772-8cfe-c0b71d8ca5c6', 'b16017b9-0237-439b-bf11-cb65f4a7d1cf',
    '856a5a5f-ee12-4776-adac-a82239984017', '56cbe4eb-206f-4900-a2c7-cb0313c62e4d',
    '0afcd385-af36-4b0f-83e4-6f9bfb1506a1', 'b06b9c8c-b1db-46a4-83a3-4f12c3fca8a6',
    '48483ccd-e9a3-4347-b188-d3cdd5284fd7', '82aba6e4-c386-49f7-9462-66908a67ff26',
    '7f822bf0-02b5-460c-aa60-ec7cb02af5f5', '3c4232b2-d2de-4682-916a-c38fe3bd0efc',
    '2410c9f2-2c23-4f08-bd7a-75b502ada8c5', '772139d4-64c5-4c11-8d53-3a502c0df597',
    '701e37ef-fc47-46fe-bdea-7aa650734196', 'eb5fc108-ea27-4163-bca7-b2b0e3d7a1c0',
    '42b16eeb-37f7-4226-945d-755983c2c5bd', '01cdfac9-aeda-49d2-8c3a-07f72ebcf81c',
    'a422b1da-09a9-415c-8350-3747d530ee95', 'e67959a8-38a7-463b-8178-9e3242a85553',
    '027bf5d4-8078-47ae-ab5c-b18b58883aa9', '91e38ef2-d618-473e-9928-c0ffeba3599b',
    'caea93d3-16ff-4146-b3e7-d3461d540965', '1b52cbc7-4e90-4691-a80d-a72cb57dcc85',
    '3906955c-2300-4647-a01e-b156d4a909dc',
    '0049cd2b-fb3f-4f35-b63e-230cd066becd', '04f08d59-10c2-43e8-90df-471123fadae7',
    '04f489d5-813d-4221-8ca8-6b6dbc47e1b1', '06d27069-6923-4037-95c4-7206a41c6b81',
    '0cc13475-597b-40e8-9a64-550f35f63a0f', '0ef32d33-6dc6-4e5b-8e52-5ba1e6826e0f',
    '11c5b41c-9bb8-4541-9262-7f065708f390', '1254b9fa-ebda-4f35-8687-11546a0a4ed4',
    '13afe600-d76b-4237-862c-391a52419b83', '1c9d5cdd-c200-40d6-b503-b2bf5a84e8b1',
    '1d0cb369-3220-4964-9178-9fecc3333794', '1e5f8206-0ec3-4ba9-9314-0113c3ec976c',
    '237bcd49-dc62-4f8e-b7a3-32d85241df97', '240252de-a204-497a-951e-80c941a6d87a',
    '28fc9364-fa1c-4647-a2a7-c9e16f1676fe', '33e8ae10-7091-4b24-8653-9e7cfe6b18f1',
    '37e8543f-09c5-4a50-885d-9814b493bbe2', '3cd1e5ba-7dc8-4aa3-8d39-b457a49dd03d',
    '3de44b84-84b2-41cd-85fa-33909effbd36', '3deb15c7-a147-4c3a-a80f-73fba5235fd3',
    '409d4bbc-5e70-45f4-a44c-8a4a54f03f0d', '428de4d1-01d9-4455-bddd-d3c13d7a88ca',
    '45daf060-5e8c-4b48-803b-de744aac1387', '450b1707-8e8f-48ce-b6cd-3ef1e9ce5e7a',
    '464f1309-5dbf-4859-a421-f887c49b4291', '46ca99c3-ce10-4016-9c35-316a17f62180',
    '4b3084fa-0a43-4065-a315-7c7e8d03b67d', '50036228-8638-4222-91eb-0d61646cb470',
    '59c3b07f-fc8a-4972-89e2-ddd103a40912',
    '609597eb-2d11-4ca4-ba9e-164fcd5d2c61', '612da05f-6173-4dd3-b55d-400eecb71102',
    '68826e1b-6068-42ee-8f68-892c22a80525', '6afc0c35-cc69-4cb8-9747-0846dc4e1a2b',
    '6b03e686-e178-4702-a078-9ef841e8b571', '6bc422d2-e3c9-4b87-88f3-a708e0e7ee2f',
}

# Read the rest of BASELINE_UUIDS from the full _rm_find_new2 set.
# This is intentionally a superset — we'll load it at module time from the
# agent file if a more complete set is needed, but the set above covers the
# Engine Room + inventory.  Additional UUIDs can be added via
# ``RESave.add_baseline_uuids()``.


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class NewDeviceInfo:
    """A device found in the RE save that is not in the baseline."""
    uuid: str
    type_id: int
    location: Optional[int]
    port_count: int
    dev_data_keys: List[str] = field(default_factory=list)


@dataclass
class ProbeMatch:
    """Result of matching a wire UUID against the probe table."""
    probe_name: str          # e.g. 'IN_3', 'VD_0', 'VM_1'
    probe_kind: str          # 'input', 'output', 'vector_input', etc.
    probe_value: Optional[int] = None  # constant value for IN_N probes


@dataclass
class WireEndpoint:
    """The other end of a wire: who else owns it."""
    device_uuid: str
    port_key: str
    device_type: int
    device_type_name: str    # human-readable from _CHILD_TYPE_NAMES or type=N


@dataclass
class PortInfo:
    """Complete information about one port of a target device."""
    port_key: str
    child_type: int
    child_type_name: str
    wire_uuid: str
    probe: Optional[ProbeMatch]
    other_ends: List[WireEndpoint] = field(default_factory=list)
    inferred_direction: str = 'unknown'    # 'input' | 'output' | 'power' | 'drive' | 'vector' | 'unknown'

    def semantic_label(self) -> str:
        """Return a suggested PORT_* constant name."""
        if self.probe:
            return self.probe.probe_name
        if self.child_type in (3, 2):
            return 'POWER'
        if self.child_type in (139, 156, 157):
            return 'DRIVE'
        if self.child_type == 142:
            return 'VECTOR'
        return f'PORT_{self.port_key}'


@dataclass
class FrameChildInfo:
    """A single child entry from a type=1 room frame's indexedChildren."""
    port_key: str
    child_type: int
    child_uuid: str
    position: Optional[Tuple[float, float, float]] = None
    rotation: Optional[Tuple[float, float, float, float]] = None

    @property
    def connection_kind(self) -> Optional[str]:
        """Human-readable kind, or None if child_type is not a cable type."""
        return CONNECTION_KINDS.get(self.child_type)


@dataclass
class FrameSnapshot:
    """Snapshot of all type=1 frame children at a location.

    Used as a baseline for :meth:`RESave.frame_diff` — take a snapshot before
    the user adds a cable, then diff after they save.
    """
    location: int
    frame_children: Dict[str, Dict[str, FrameChildInfo]]  # frame_uuid -> {port_key -> info}

    @property
    def all_port_keys(self) -> Dict[str, set]:
        """Return {frame_uuid -> set of port_key strings}."""
        return {fu: set(children.keys()) for fu, children in self.frame_children.items()}

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict for persistence."""
        frames = {}
        for fu, children in self.frame_children.items():
            frames[fu] = {}
            for pk, info in children.items():
                entry: Dict[str, Any] = {
                    'child_type': info.child_type,
                    'child_uuid': info.child_uuid,
                }
                if info.position is not None:
                    entry['position'] = list(info.position)
                if info.rotation is not None:
                    entry['rotation'] = list(info.rotation)
                frames[fu][pk] = entry
        return {'location': self.location, 'frame_children': frames}

    @classmethod
    def from_dict(cls, data: dict) -> 'FrameSnapshot':
        """Deserialize from a dict produced by :meth:`to_dict`."""
        frame_children: Dict[str, Dict[str, FrameChildInfo]] = {}
        for fu, children in data['frame_children'].items():
            frame_children[fu] = {}
            for pk, entry in children.items():
                pos = tuple(entry['position']) if 'position' in entry else None
                rot = tuple(entry['rotation']) if 'rotation' in entry else None
                frame_children[fu][pk] = FrameChildInfo(
                    port_key=pk,
                    child_type=entry['child_type'],
                    child_uuid=entry['child_uuid'],
                    position=pos,
                    rotation=rot,
                )
        return cls(location=data['location'], frame_children=frame_children)


@dataclass
class FrameDiffEntry:
    """A new child that appeared on a room frame since a baseline snapshot."""
    frame_uuid: str
    child: FrameChildInfo


@dataclass
class FramePortRef:
    """One side of a room connection — a specific frame's port key for a shared node."""
    frame_uuid: str
    port_key: str


@dataclass
class RoomConnection:
    """A connection node shared between two or more room sub-frames.

    When a cable (power, data, or vector) connects two wall sockets in the
    same room, the game creates a node (type=2, 3, 4, 5, or 142) that appears
    as a child of *two* different type=1 room frames with different port keys.
    Each node has a unique position and rotation identifying the physical socket.
    """
    node_uuid: str
    node_type: int
    connection_kind: str       # 'large_power', 'small_power', 'large_data', 'small_data', 'vector'
    frame_refs: List[FramePortRef]
    position: Optional[Tuple[float, float, float]] = None
    rotation: Optional[Tuple[float, float, float, float]] = None


@dataclass
class RoomConnectionMap:
    """All shared connection nodes detected at a specific save location.

    A shared node is a child UUID that appears in ``indexedChildren`` of two
    or more type=1 room frames at the same ``location`` value.  These represent
    physical cable endpoints (wall sockets) in the game.
    """
    location: int
    frames: Dict[str, int]                     # frame_uuid -> child_count
    connections: List[RoomConnection] = field(default_factory=list)

    def by_kind(self, kind: str) -> List[RoomConnection]:
        """Return connections filtered to a single connection kind."""
        return [c for c in self.connections if c.connection_kind == kind]

    def by_frame(self, frame_uuid_prefix: str) -> List[RoomConnection]:
        """Return connections involving a specific frame (prefix match)."""
        return [c for c in self.connections
                if any(r.frame_uuid.startswith(frame_uuid_prefix) for r in c.frame_refs)]

    def hub_frame(self, kind: str) -> Optional[str]:
        """If all connections of a kind share one common frame, return its UUID.

        When every shared node of a given kind has the same frame on one side,
        that frame likely represents the Room itself (or a bus sub-frame) for
        that connection type.  Returns ``None`` if no single frame spans all
        connections, or if there are no connections of that kind.
        """
        conns = self.by_kind(kind)
        if not conns:
            return None
        frame_counts: Dict[str, int] = {}
        for c in conns:
            for ref in c.frame_refs:
                frame_counts[ref.frame_uuid] = frame_counts.get(ref.frame_uuid, 0) + 1
        for frame_uuid, count in frame_counts.items():
            if count == len(conns):
                return frame_uuid
        return None

    def kinds_present(self) -> List[str]:
        """Return the distinct connection kinds that have at least one connection."""
        return sorted({c.connection_kind for c in self.connections})


# ---------------------------------------------------------------------------
# Save file primitives (JSON walk, wire ownership)
# ---------------------------------------------------------------------------

def flatten_save(data: Any) -> Dict[str, dict]:
    """Recursively walk a deserialized save JSON and index every node by UUID."""
    by_uuid: Dict[str, dict] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            uid = node.get('uuid')
            if uid is not None:
                by_uuid[uid] = node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return by_uuid


def build_wire_owners(by_uuid: Dict[str, dict]) -> Dict[str, List[Tuple[str, str, int]]]:
    """Build reverse map: wire_uuid -> [(owner_uuid, port_key, owner_type)]."""
    wire_owners: Dict[str, List[Tuple[str, str, int]]] = {}
    for dev_uuid, dev in by_uuid.items():
        for port_key, child in (dev.get('indexedChildren') or {}).items():
            if isinstance(child, dict) and 'uuid' in child:
                wire_owners.setdefault(child['uuid'], []).append(
                    (dev_uuid, str(port_key), dev.get('type', 0))
                )
    return wire_owners


def match_probe(wire_uuid: str) -> Optional[ProbeMatch]:
    """Match a wire UUID against the probe wire table."""
    entry = PROBE_WIRES.get(wire_uuid)
    if entry is None:
        return None
    return ProbeMatch(
        probe_name=entry['name'],
        probe_kind=entry['kind'],
        probe_value=entry.get('value'),
    )


def get_fbs_stored_values(by_uuid: Dict[str, dict]) -> Dict[str, int]:
    """Extract FourBitSwitch stored signal values: device_uuid -> int."""
    result: Dict[str, int] = {}
    for dev_uuid, dev in by_uuid.items():
        if dev.get('type') != 42:
            continue
        for v in (dev.get('indexedDeviceData') or {}).values():
            if isinstance(v, dict) and 'signal' in v:
                result[dev_uuid] = v['signal']
                break
    return result


# ---------------------------------------------------------------------------
# RESave — high-level RE session
# ---------------------------------------------------------------------------

class RESave:
    """High-level interface for reverse-engineering device ports.

    Loads the fixed RE save on construction and provides methods for
    new-device detection, port mapping, and probe matching.
    """

    def __init__(self, save_path: Optional[str] = None) -> None:
        self._path = Path(save_path) if save_path else RE_SAVE_PATH
        self._load()
        self._baseline = set(BASELINE_UUIDS)

    def _load(self) -> None:
        """Read the save JSON and rebuild internal indices."""
        with open(self._path, encoding='utf-8') as f:
            self._data = json.load(f)
        self._by_uuid = flatten_save(self._data)
        self._wire_owners = build_wire_owners(self._by_uuid)
        self._fbs_stored = get_fbs_stored_values(self._by_uuid)

    def reload(self) -> None:
        """Re-read the save file from disk.

        Call this after the user saves in-game so that :meth:`frame_diff`
        and other queries reflect the latest data.
        """
        self._load()

    @property
    def by_uuid(self) -> Dict[str, dict]:
        return self._by_uuid

    @property
    def wire_owners(self) -> Dict[str, List[Tuple[str, str, int]]]:
        return self._wire_owners

    # -- Baseline management -----------------------------------------------

    def add_baseline_uuids(self, uuids: Set[str]) -> None:
        """Extend the baseline set (e.g. after adding new probe devices)."""
        self._baseline.update(uuids)

    def update_baseline_from_save(self) -> Set[str]:
        """Set baseline to ALL UUIDs currently in the save. Returns the set."""
        self._baseline = set(self._by_uuid.keys())
        return self._baseline

    # -- New device detection ----------------------------------------------

    def find_new_devices(self) -> List[NewDeviceInfo]:
        """Return devices in the save that are not in the baseline set."""
        results: List[NewDeviceInfo] = []
        for uid, node in self._by_uuid.items():
            if uid in self._baseline:
                continue
            type_id = node.get('type')
            if not isinstance(type_id, int):
                continue
            children = node.get('indexedChildren') or {}
            dev_data = node.get('indexedDeviceData') or {}
            results.append(NewDeviceInfo(
                uuid=uid,
                type_id=type_id,
                location=node.get('location'),
                port_count=len(children),
                dev_data_keys=list(dev_data.keys()),
            ))
        results.sort(key=lambda d: (d.type_id, d.uuid))
        return results

    def find_new_of_type(self, type_id: int) -> List[NewDeviceInfo]:
        """Find new devices of a specific type."""
        return [d for d in self.find_new_devices() if d.type_id == type_id]

    def print_new_devices(self) -> None:
        """Pretty-print all new (non-baseline) devices."""
        new = self.find_new_devices()
        if not new:
            print('No new devices found (all match baseline).')
            return
        print(f'New devices: {len(new)}\n')
        for d in new:
            dd_str = f'  devData keys: {d.dev_data_keys}' if d.dev_data_keys else ''
            print(f'  type={d.type_id:<4d}  uuid={d.uuid[:8]}  loc={d.location}  ports={d.port_count}{dd_str}')

    # -- Port mapping ------------------------------------------------------

    def port_map(self, type_id: Optional[int] = None, uuid_prefix: Optional[str] = None) -> List[PortInfo]:
        """Enumerate ports for device(s) matching type_id or uuid_prefix.

        Returns one PortInfo per port across all matching devices.
        At least one of type_id or uuid_prefix must be specified.
        """
        targets = self._find_targets(type_id, uuid_prefix)
        results: List[PortInfo] = []
        for uid, node in targets:
            for port_key, child in sorted(
                (node.get('indexedChildren') or {}).items(),
                key=lambda x: int(x[0]) if str(x[0]).lstrip('-').isdigit() else 0,
            ):
                child_type = child.get('type', 0)
                wire_uuid = child.get('uuid', '')
                probe = match_probe(wire_uuid)

                # Find other devices on this wire
                others: List[WireEndpoint] = []
                for owner_uuid, owner_key, owner_type in self._wire_owners.get(wire_uuid, []):
                    if owner_uuid == uid:
                        continue
                    others.append(WireEndpoint(
                        device_uuid=owner_uuid,
                        port_key=owner_key,
                        device_type=owner_type,
                        device_type_name=_CHILD_TYPE_NAMES.get(owner_type, f'type={owner_type}'),
                    ))

                direction = self._infer_direction(child_type, probe, others)
                results.append(PortInfo(
                    port_key=str(port_key),
                    child_type=child_type,
                    child_type_name=_CHILD_TYPE_NAMES.get(child_type, f'type={child_type}'),
                    wire_uuid=wire_uuid,
                    probe=probe,
                    other_ends=others,
                    inferred_direction=direction,
                ))
        return results

    def print_port_map(self, type_id: Optional[int] = None, uuid_prefix: Optional[str] = None) -> None:
        """Pretty-print port map with probe annotations."""
        targets = self._find_targets(type_id, uuid_prefix)
        if not targets:
            print(f'No devices found for type_id={type_id} uuid_prefix={uuid_prefix}')
            return

        for uid, node in targets:
            print(f'\ntype={node.get("type")}  uuid={uid[:8]}')
            dd = node.get('indexedDeviceData') or {}
            if dd:
                for k, v in list(dd.items())[:6]:
                    print(f'  devData key={k}  val={v}')

            ports = self.port_map(uuid_prefix=uid[:8])
            for p in ports:
                probe_str = ''
                if p.probe:
                    val_str = f' value={p.probe.probe_value}' if p.probe.probe_value is not None else ''
                    probe_str = f' [{p.probe.probe_name}{val_str}]'

                other_strs = []
                for o in p.other_ends:
                    stored = self._fbs_stored.get(o.device_uuid)
                    stored_str = f' stored={stored}' if stored is not None else ''
                    other_strs.append(f'{o.device_type_name}({o.device_uuid[:8]} key={o.port_key}{stored_str})')
                other_info = ', '.join(other_strs) if other_strs else '[unwired]'

                print(f'  port_key={p.port_key:>15}  child={p.child_type}({p.child_type_name})'
                      f'  dir={p.inferred_direction:<7s}{probe_str}  -> {other_info}')

    def port_constants(self, type_id: Optional[int] = None, uuid_prefix: Optional[str] = None) -> str:
        """Generate Python PORT_* constant assignments from port map.

        Returns a string suitable for pasting into a device class.
        """
        ports = self.port_map(type_id=type_id, uuid_prefix=uuid_prefix)
        lines: List[str] = []
        seen_labels: Dict[str, int] = {}
        for p in ports:
            if p.probe:
                if p.probe.probe_kind in ('input', 'vector_input', 'large_input'):
                    label = f'PORT_INPUT_{p.probe.probe_name}'
                elif p.probe.probe_kind in ('output', 'vector_output', 'large_output'):
                    label = f'PORT_OUTPUT_{p.probe.probe_name}'
                else:
                    label = f'PORT_{p.probe.probe_name}'
            elif p.inferred_direction == 'power':
                label = 'PORT_POWER'
            elif p.inferred_direction == 'drive':
                label = 'PORT_DRIVE'
            elif p.inferred_direction == 'vector':
                label = 'PORT_VECTOR'
            else:
                label = f'PORT_{p.port_key}'

            # Deduplicate labels
            if label in seen_labels:
                seen_labels[label] += 1
                label = f'{label}_{seen_labels[label]}'
            else:
                seen_labels[label] = 0

            comment = f'  # {p.probe.probe_name}' if p.probe else f'  # child_type={p.child_type}'
            lines.append(f"{label} = '{p.port_key}'{comment}")
        return '\n'.join(lines)

    # -- Census (cross-save type frequency) --------------------------------

    def census_unknown_types(self, saves_dir: Optional[str] = None) -> List[Tuple[int, int, str]]:
        """Scan saves for unknown type IDs not registered in DeviceClasses.

        Returns list of (type_id, count, example_path) sorted by descending count.
        """
        from ifetchrocks_sim.stub_generator import scan_all_saves, DEVICE_CLASS_LOOKUP, TYPE_NAME_LOOKUP

        saves = Path(saves_dir) if saves_dir else RE_SAVE_PATH.parent
        known_types: Set[int] = set()
        for name, value in TYPE_NAME_LOOKUP.items():
            if isinstance(value, int):
                known_types.add(value)
        # Also add types that have DeviceClasses entries
        for name in DEVICE_CLASS_LOOKUP:
            if name in TYPE_NAME_LOOKUP:
                v = TYPE_NAME_LOOKUP[name]
                if isinstance(v, int):
                    known_types.add(v)

        from collections import Counter
        counts: Counter = Counter()
        examples: Dict[int, str] = {}
        for component in scan_all_saves(saves):
            t = component.get('type')
            if isinstance(t, int) and t not in known_types:
                counts[t] += 1
                if t not in examples:
                    examples[t] = 'RE save'

        results = [(t, c, examples.get(t, '')) for t, c in counts.most_common()]
        return results

    # -- Internal helpers --------------------------------------------------

    def _find_targets(
        self,
        type_id: Optional[int],
        uuid_prefix: Optional[str],
    ) -> List[Tuple[str, dict]]:
        """Find devices matching type_id and/or uuid_prefix."""
        results: List[Tuple[str, dict]] = []
        for uid, node in self._by_uuid.items():
            node_type = node.get('type')
            if not isinstance(node_type, int):
                continue
            if type_id is not None and node_type != type_id:
                continue
            if uuid_prefix is not None and not uid.startswith(uuid_prefix):
                continue
            if node.get('indexedChildren'):
                results.append((uid, node))
        return results

    @staticmethod
    def _infer_direction(
        child_type: int,
        probe: Optional[ProbeMatch],
        others: List[WireEndpoint],
    ) -> str:
        """Infer port direction from child type and probe match."""
        if child_type in (3, 2):
            return 'power'
        if child_type in (139, 156, 157):
            return 'drive'
        if child_type == 142:
            return 'vector'
        if probe:
            if probe.probe_kind in ('input', 'vector_input', 'large_input'):
                return 'input'
            if probe.probe_kind in ('output', 'vector_output', 'large_output'):
                return 'output'
        # Heuristic: if other end is a FourBitSwitch/ControllerDial → this is an input
        for o in others:
            if o.device_type in (42, 78):  # FourBitSwitch, ControllerDial
                return 'input'
            if o.device_type in (71, 122):  # ValueDisplay, BinaryLightArray
                return 'output'
        return 'unknown'

    # -- Frame snapshot / diff ---------------------------------------------

    def frame_snapshot(self, location: int) -> FrameSnapshot:
        """Capture all type=1 frame children at *location*.

        Returns a :class:`FrameSnapshot` that can be passed to
        :meth:`frame_diff` after the user adds a cable and saves.
        """
        frame_children: Dict[str, Dict[str, FrameChildInfo]] = {}
        for uid, node in self._by_uuid.items():
            if node.get('type') != 1 or node.get('location') != location:
                continue
            children: Dict[str, FrameChildInfo] = {}
            for port_key, child in (node.get('indexedChildren') or {}).items():
                if not isinstance(child, dict):
                    continue
                child_uuid = child.get('uuid', '')
                child_type = child.get('type', 0)
                pos = child.get('position')
                rot = child.get('rotation')
                position = None
                rotation = None
                if isinstance(pos, dict):
                    try:
                        position = (float(pos['x']), float(pos['y']), float(pos['z']))
                    except (KeyError, TypeError, ValueError):
                        pass
                if isinstance(rot, dict):
                    try:
                        rotation = (float(rot['x']), float(rot['y']),
                                    float(rot['z']), float(rot['w']))
                    except (KeyError, TypeError, ValueError):
                        pass
                children[str(port_key)] = FrameChildInfo(
                    port_key=str(port_key),
                    child_type=child_type,
                    child_uuid=child_uuid,
                    position=position,
                    rotation=rotation,
                )
            frame_children[uid] = children
        return FrameSnapshot(location=location, frame_children=frame_children)

    @staticmethod
    def _baseline_path(location: int) -> Path:
        """Return the default file path for a persisted frame baseline."""
        return RE_SAVE_PATH.parent / f'.re_frame_baseline_{location}.json'

    def save_frame_baseline(self, location: int, path: Optional[str] = None) -> Path:
        """Snapshot current frames at *location* and persist to disk.

        Returns the path written.  The default location is next to the save
        files: ``game_app_data/Saves/.re_frame_baseline_<loc>.json``.
        """
        snap = self.frame_snapshot(location)
        out = Path(path) if path else self._baseline_path(location)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(snap.to_dict(), f, indent=1)
        print(f'Baseline saved: {out}  ({sum(len(c) for c in snap.frame_children.values())} port keys across {len(snap.frame_children)} frames)')
        return out

    def load_frame_baseline(self, location: int, path: Optional[str] = None) -> FrameSnapshot:
        """Load a previously persisted frame baseline from disk."""
        src = Path(path) if path else self._baseline_path(location)
        with open(src, encoding='utf-8') as f:
            return FrameSnapshot.from_dict(json.load(f))

    def frame_diff(self, location: int, baseline: Optional[FrameSnapshot] = None) -> List[FrameDiffEntry]:
        """Compare current frame children at *location* against *baseline*.

        If *baseline* is ``None``, auto-loads from the default persisted
        baseline file (written by :meth:`save_frame_baseline`).  Raises
        ``FileNotFoundError`` if no persisted baseline exists.

        Returns a list of :class:`FrameDiffEntry` for port keys present now
        but not in the baseline.  Also detects entirely new frames.
        """
        if baseline is None:
            baseline = self.load_frame_baseline(location)
        current = self.frame_snapshot(location)
        results: List[FrameDiffEntry] = []
        for frame_uuid, children in current.frame_children.items():
            old_keys = set(baseline.frame_children.get(frame_uuid, {}).keys())
            for port_key, info in children.items():
                if port_key not in old_keys:
                    results.append(FrameDiffEntry(frame_uuid=frame_uuid, child=info))
        results.sort(key=lambda e: (e.frame_uuid, e.child.port_key))
        return results

    def print_frame_diff(self, location: int, baseline: Optional[FrameSnapshot] = None) -> None:
        """Pretty-print new frame children since *baseline*.

        If *baseline* is ``None``, auto-loads from disk.
        """
        diff = self.frame_diff(location, baseline)
        if not diff:
            print('No new frame children detected.')
            return
        print(f'New frame children at location={location} ({len(diff)}):')
        for entry in diff:
            kind = entry.child.connection_kind or f'type={entry.child.child_type}'
            pos_str = ''
            if entry.child.position:
                p = entry.child.position
                pos_str = f'  pos=({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f})'
            print(f'  frame={entry.frame_uuid[:8]}  key={entry.child.port_key}'
                  f'  {kind}  uuid={entry.child.child_uuid[:8]}{pos_str}')

    # -- Room connection detection -----------------------------------------

    def room_connections(self, location: int) -> RoomConnectionMap:
        """Detect shared connection nodes between type=1 room frames at *location*.

        Scans all type=1 nodes whose ``location`` field equals *location*,
        then finds child UUIDs that appear in the ``indexedChildren`` of two
        or more frames.  Each such shared child is classified by its
        ``child_type`` into a connection kind (large_power, small_power,
        large_data, small_data, vector).

        Returns a :class:`RoomConnectionMap` with structured results.
        """
        # 1. Collect all type=1 frames at this location
        frames: Dict[str, dict] = {}   # frame_uuid -> node
        for uid, node in self._by_uuid.items():
            if node.get('type') != 1:
                continue
            if node.get('location') != location:
                continue
            frames[uid] = node

        # 2. Build child_uuid -> [(frame_uuid, port_key, child_type)]
        child_to_frames: Dict[str, List[Tuple[str, str, int]]] = {}
        for frame_uuid, node in frames.items():
            for port_key, child in (node.get('indexedChildren') or {}).items():
                if not isinstance(child, dict) or 'uuid' not in child:
                    continue
                child_uuid = child['uuid']
                child_type = child.get('type', 0)
                child_to_frames.setdefault(child_uuid, []).append(
                    (frame_uuid, str(port_key), child_type)
                )

        # 3. Keep only children referenced by 2+ frames with a known connection kind
        connections: List[RoomConnection] = []
        for child_uuid, refs in child_to_frames.items():
            if len(refs) < 2:
                continue
            # All refs should agree on child_type; use the first
            child_type = refs[0][2]
            kind = CONNECTION_KINDS.get(child_type)
            if kind is None:
                continue    # not a cable/wire type we track

            # Extract position/rotation from the child node
            child_node = self._by_uuid.get(child_uuid, {})
            pos = child_node.get('position')
            rot = child_node.get('rotation')
            position = None
            rotation = None
            if isinstance(pos, dict):
                try:
                    position = (float(pos['x']), float(pos['y']), float(pos['z']))
                except (KeyError, TypeError, ValueError):
                    pass
            if isinstance(rot, dict):
                try:
                    rotation = (float(rot['x']), float(rot['y']),
                                float(rot['z']), float(rot['w']))
                except (KeyError, TypeError, ValueError):
                    pass

            frame_refs = [FramePortRef(frame_uuid=r[0], port_key=r[1]) for r in refs]
            connections.append(RoomConnection(
                node_uuid=child_uuid,
                node_type=child_type,
                connection_kind=kind,
                frame_refs=frame_refs,
                position=position,
                rotation=rotation,
            ))

        connections.sort(key=lambda c: (c.connection_kind, c.node_uuid))

        frame_summary = {uid: len((node.get('indexedChildren') or {}))
                         for uid, node in frames.items()}

        return RoomConnectionMap(
            location=location,
            frames=frame_summary,
            connections=connections,
        )

    def print_room_connections(self, location: int) -> None:
        """Pretty-print shared connection nodes at *location*."""
        rcm = self.room_connections(location)
        print(f'\nRoom connections at location={location}')
        print(f'Frames ({len(rcm.frames)}):')
        for uid, count in sorted(rcm.frames.items()):
            print(f'  {uid[:8]}  children={count}')

        if not rcm.connections:
            print('\nNo shared connection nodes found.')
            return

        for kind in rcm.kinds_present():
            conns = rcm.by_kind(kind)
            hub = rcm.hub_frame(kind)
            hub_str = f'  [hub frame: {hub[:8]}]' if hub else ''
            print(f'\n{kind} ({len(conns)} shared nodes){hub_str}')
            for c in conns:
                pos_str = ''
                if c.position:
                    pos_str = f'  pos=({c.position[0]:.3f}, {c.position[1]:.3f}, {c.position[2]:.3f})'
                refs_str = ' <-> '.join(
                    f'{r.frame_uuid[:8]} key={r.port_key}' for r in c.frame_refs
                )
                print(f'  {c.node_uuid[:8]}  {refs_str}{pos_str}')
