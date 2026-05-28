# i-fetch-rocks-sim

A Python package for loading, inspecting, and simulating **I Fetch Rocks** save files.

The package reconstructs the in-game wire diagram from a save file as a Python object graph and lets you:

- **Inspect** rooms, devices, and wires without loading the game.
- **Visualise** the wire network as an interactive HTML graph.
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

# Returns a structured SaveModel
save = reader.load_save_path("path/to/save.json")

print(save.ship.component_count())  # total component nodes
print(len(save.ship.rooms))         # room count
print(len(save.ship.floating))      # floating device count

# Or get a quick summary
summary = reader.load_path("path/to/save.json")
print(summary.room_count, summary.floating_count, summary.device_count)
```

---

## Generating an HTML wire-graph

The simulator can reconstruct the full wire network and export it as an interactive HTML graph
powered by [pyvis](https://pyvis.readthedocs.io/). Install the optional dependency first:

```powershell
pip install ifetchrocks-sim[graph]
```

Then generate the graph:

```python
from ifetchrocks_sim import SimulatorFacade

sim = SimulatorFacade()
sim.load_save("path/to/save.json")

# Build graph for specific rooms, or pass [] for all rooms
graph = sim.build_graph(room_filters=["LIFE_SUPPORT", "HELM"])
graph.write_html("wiring.html")
```

Open `wiring.html` in any browser to explore the interactive node graph.

- Green edges = input signals flowing into a device.
- Purple edges = output signals leaving a device.
- Thick edges = large-bus (16-element array) connections.

To include or exclude power wires:

```python
graph = sim.build_graph(room_filters=[], show_power_wires=False)
```

---

## Simulating ticks

The simulator runs the wire network reactively. Advancing a tick fires end-of-tick
and start-of-tick listeners (loop-break latching), then propagates all signal changes
until the network is quiescent.

```python
from ifetchrocks_sim import SimulatorFacade

sim = SimulatorFacade()
sim.load_save("path/to/save.json")

# Register wires to record
sim.capture_uuid("abcd1234-...")   # full UUID or prefix

# Optionally inject a value into a wire before each tick
# sim.inject("wire-uuid-prefix", value)

for tick in range(20):
    sim.set_tick(tick)

# Read captured values: {tick: {wire_uuid: [values]}}
capture = sim.get_capture()
for tick, wires in sorted(capture.items()):
    for wire_uuid, values in wires.items():
        print(f"tick={tick}  wire={wire_uuid[:8]}  values={values}")
```

### Wire tracing

Trace signal ancestry and downstream consumers:

```python
# What drives this wire?
sim.print_backtrace("abcd1234")

# What does this wire feed?
sim.print_forwardtrace("abcd1234")

# Find a path between two wires
path = sim.find_signal_path("source-prefix", "target-prefix")
```

### Wire diff

Compare wire state before and after a stimulus:

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

# Save and reload labels across sessions
sim.save_labels("my_labels.json")
sim.load_labels("my_labels.json")
```

---

## Room and device inventory

```python
# List all rooms and their ports
for room, ports in sim.room_port_summary().items():
    print(room, len(ports), "ports")

# Find unimplemented/unknown devices in the save
for entry in sim.list_unknown_devices():
    print(entry.type_id, entry.uuid[:8], entry.room)

# Compare two saves
diff = sim.diff_saves("before.json", "after.json")
print(diff.device_count_deltas)
print(diff.room_port_diffs)
```

---

## Development

```powershell
.venv\Scripts\pytest          # run tests
.venv\Scripts\ruff check .    # lint
```

See [MIGRATION.md](MIGRATION.md) for the phased plan to migrate the full simulator from the source project.

---

## License

MIT — see [LICENSE](LICENSE).
