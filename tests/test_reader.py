import json

from ifetchrocks_sim import SaveReader


def test_load_payload_counts_components():
    payload = {
        "ship": {
            "rooms": [
                {
                    "type": 1,
                    "children": [
                        {"type": 5, "children": []},
                        {"type": 5, "children": []},
                    ],
                }
            ],
            "floating": [{"type": 2, "children": []}],
        }
    }

    summary = SaveReader().load_payload(payload)

    assert summary.room_count == 1
    assert summary.floating_count == 1
    assert summary.device_count == 4


def test_load_path(tmp_path):
    p = tmp_path / "save.json"
    p.write_text(json.dumps({"ship": {"rooms": [], "floating": []}}), encoding="utf-8")

    summary = SaveReader().load_path(p)

    assert summary.room_count == 0
    assert summary.floating_count == 0
    assert summary.device_count == 0


def test_parse_payload_returns_structured_models():
    payload = {
        "ship": {
            "rooms": [
                {
                    "type": 1,
                    "uuid": "room-1",
                    "children": [{"type": 5, "uuid": "wire-1", "children": []}],
                    "indexedChildren": {
                        "0": {"type": 3, "uuid": "power-1", "children": []},
                        "1": None,
                    },
                }
            ],
            "floating": [],
        }
    }

    save = SaveReader().parse_payload(payload)

    assert len(save.ship.rooms) == 1
    room = save.ship.rooms[0]
    assert room.type_id == 1
    assert room.uuid == "room-1"
    assert len(room.children) == 1
    assert room.children[0].uuid == "wire-1"
    assert "0" in room.indexed_children
    assert room.indexed_children["0"].uuid == "power-1"
    assert save.ship.component_count() == 3


def test_load_save_path(tmp_path):
    p = tmp_path / "save.json"
    p.write_text(
        json.dumps(
            {
                "ship": {
                    "rooms": [{"type": 1, "uuid": "r", "children": []}],
                    "floating": [{"type": 2, "uuid": "f", "children": []}],
                }
            }
        ),
        encoding="utf-8",
    )

    save = SaveReader().load_save_path(p)

    assert len(save.ship.rooms) == 1
    assert len(save.ship.floating) == 1
    assert save.ship.component_count() == 2
