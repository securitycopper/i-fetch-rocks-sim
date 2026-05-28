# i-fetch-rocks-sim

A Python package for loading, inspecting, and simulating **I Fetch Rocks** save files.

**Published on PyPI:** https://pypi.org/project/ifetchrocks-sim/

The package reconstructs the in-game wire diagram from a save file as a Python object graph and lets you:

- **Inspect** rooms, devices, and wires without loading the game.
- **Visualise** the wire network as an interactive HTML graph (powered by [pyvis](https://pyvis.readthedocs.io/)).
- **Simulate** the circuit tick-by-tick to capture signal values and trace behaviour.

---

## Install

```powershell
pip install ifetchrocks-sim
```

Or for local/editable development:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -e .[dev]
```

---

## Reading a save file

Load a save and inspect the structured ship model:

```python
from ifetchrocks_sim import SaveReader

reader = SaveReader()
save = reader.load_save_path("path/to/save.json")

print(save.ship.component_count())  # total component nodes
print(len(save.ship.rooms))         # room count
print(len(save.ship.floating))      # floating device count

summary = reader.load_path("path/to/save.json")
print(summary.room_count, summary.floating_count, summary.device_count)
```

---

## Simulating ticks

```python
from ifetchrocks_sim import Simulator

sim = Simulator()
with open("path/to/save.json") as f:
    sim.load_from_file(f)

# Record wire values across ticks
sim.capture_uuid("abcd1234-...")   # full UUID or unique prefix

for tick in range(20):
    sim.set_tick(tick)

# {tick: {wire_uuid: [values]}}
capture = sim.get_capture()
for tick, wires in sorted(capture.items()):
    for wire_uuid, values in wires.items():
        print(f"tick={tick}  wire={wire_uuid[:8]}  values={values}")
```

---

## Wire tracing

```python
# What drives this wire?
sim.print_backtrace("abcd1234")

# What does this wire feed?
sim.print_forwardtrace("abcd1234")

# Or use the module-level helpers directly
from ifetchrocks_sim import print_backtrace, print_forwardtrace
print_backtrace(sim, "abcd1234")

# Find a signal path between two wires
path = sim.find_signal_path("source-prefix", "target-prefix")
```

---

## Wire diff

```python
before = sim.snapshot_wire_values()
sim.set_tick(1)
after = sim.snapshot_wire_values()

for diff in sim.diff_wires(before, after):
    print(diff.uuid[:8], diff.before, "->", diff.after)
```

---

## Labelling wires and devices

```python
sim.set_wire_label("abcd1234", "program_counter")
sim.set_device_label("ffff0000", "alu_register")

sim.save_labels("my_labels.json")
sim.load_labels("my_labels.json")
```

---

## Generating an HTML wire-graph

```python
network = sim.build_graph_network(room_filters=["LIFE_SUPPORT", "HELM"])
network.write_html("wiring.html")

# All rooms, no power wires
network = sim.build_graph_network(room_filters=[], show_power_wires=False)
```

Open `wiring.html` in any browser to explore the interactive node graph.

---

## Room and device inventory

```python
# Find unimplemented/unknown devices in the save
for entry in sim.list_unknown_devices():
    print(entry.type_id, entry.uuid[:8], entry.room)

# Compare two saves
diff = sim.diff_saves("before.json", "after.json")
print(diff.device_count_deltas)
```

---

## Package layout

```
ifetchrocks_sim/
├── simulator.py          # Simulator — main entry point
├── reader.py             # SaveReader — lightweight save-file parser
├── models.py             # SaveModel, ShipModel, ComponentNode, SaveSummary
├── backtrace.py          # backtrace_wire / forwardtrace_wire helpers
├── analysis.py           # signal-change analysis utilities
├── labels.py             # LabelRegistry — wire/device label store
├── recording.py          # WireRecorder — time-series wire capture
├── re_tools.py           # reverse-engineering probe utilities
├── validation.py         # health_check — wiring sanity checks
├── cli.py                # CLI entry point (python -m ifetchrocks_sim)
├── stub_generator.py     # generate device stub skeletons
├── _drive_loader.py      # internal: load drive .bin files for MemoryBaySignal
├── devices/              # all in-game device implementations
├── network/              # DataNetwork / LargeDataNetwork / DataNetworkManager
└── testing/              # CircuitBuilder and wire assertion helpers
```

---

## Learning & References

**Reverse-engineering guides:** See [`docs/`](docs/) for:
- [Device port identification methodology](docs/reverse-engineering.md)
- [Fixed probe inventory](docs/re-probe-setup.md)
- [Reverse-engineering progress tracker](docs/unknown-devices-ship-cpu.md)
- [Ship topology and architecture](docs/ship-topology.md)
- [Room-to-room cable connections](docs/room-port-map.md)

**Agents & skills:** See [`.github/README.md`](.github/README.md) for DeviceRE, CircuitBuilder,
device-setup, and sim-diagnosis tools.

---

## Development

```powershell
.venv\Scripts\pytest          # run tests
.venv\Scripts\ruff check .    # lint
```

---

## License

MIT — see [LICENSE](LICENSE).
