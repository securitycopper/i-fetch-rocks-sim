# Copilot / Agent Instructions for ifetchrocks-sim

## Purpose

Help contributors and users build circuits, reverse-engineer devices, and diagnose
signal propagation problems in the **ifetchrocks-sim** package.

## Setup

Install the package:

```bash
pip install ifetchrocks-sim>=0.1.0
```

Or for development (from repo):

```bash
git clone https://github.com/securitycopper/i-fetch-rocks-sim
cd i-fetch-rocks-sim
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\pip install pytest
```

- **Python requirement:** 3.9+ (3.10+ for CI testing)
- **Main dependency:** pyvis>=0.3

## Quick start

### Load a save and inspect

```python
from ifetchrocks_sim import Simulator

sim = Simulator()
with open('path/to/save.json') as f:
    sim.load_from_file(f)

# Explore devices
for room, devices in sim.found_devices.items():
    print(f"{room}: {len(devices)} devices")

# Run 10 ticks
for _ in range(10):
    sim.tick()
```

### Build and test a circuit (no save file)

```python
from ifetchrocks_sim.testing import CircuitBuilder
from ifetchrocks_sim.devices.data_processing.logic import LogicalNot

cb = CircuitBuilder()
in_wire = cb.add_wire(value=1)
out_wire = cb.add_wire()
cb.add_device(LogicalNot, inputs=[in_wire], outputs=[out_wire])

cb.tick()
print(f"Output: {cb.read(out_wire)}")  # Should be 0
```

### Reverse-engineer a device

Place device in the Engine Room RE save, wire to probes, save the game, then:

```python
from ifetchrocks_sim.re_tools import RESave

re = RESave()  # Loads fixed RE save automatically
new_devices = re.find_new_devices()
re.print_port_map(type_id=new_devices[0].type_id)
```

### Diagnose signal problems

```python
# Backtrace: who drives this wire?
sim.print_backtrace('wire-prefix', max_depth=10)

# Forwardtrace: what consumes this wire?
sim.print_forwardtrace('wire-prefix', max_depth=10)

# Read current value
network = sim.find_network('wire-prefix')
value = network.get_value('full-uuid')
```

## Important files & directories

- **Core:** `src/ifetchrocks_sim/` — main package
  - Subpackages: `devices/`, `network/`, `testing/`, `sim/`, `re_tools.py`
- **Tests:** `tests/` — pytest-style unit tests
- **Saves:** `game_app_data/Saves/` — simulator save files
  - **RE save (fixed):** `102d6094-bff6-413a-b859-b4992647c9e5.json`

## Testing

Run all tests:

```bash
python -m pytest tests/ -v
```

Run a specific test:

```bash
python -m pytest tests/test_circuit_example.py::TestCircuitExample::test_some_behaviour -v
```

## Coding conventions

- Keep all changes in `src/ifetchrocks_sim/` (device implementations, core API)
- Add tests to `tests/` (pytest style)
- Follow existing device structure (inherit from `Device`, use `DataNetworkManager`)
- Use public API only; no private paths

## Agents & Skills

See `.github/README.md` for available agents and skills:

- **DeviceRE** — reverse-engineer a new device after placing it in-game
- **CircuitBuilder** — design and test circuits without save files
- **device-setup** — port ID extraction and device implementation guidance
- **sim-diagnosis** — backtrace, forwardtrace, and signal analysis tools

## Common tasks

### Add a new device type

1. Inspect the device in-game using **DeviceRE** agent
2. Identify port IDs with **device-setup** skill
3. Implement device class in `src/ifetchrocks_sim/devices/<category>/`
4. Register in `src/ifetchrocks_sim/simulator.py`
5. Test with **CircuitBuilder** agent
6. Run full suite: `pytest tests/ -v`

### Test a circuit

Use **CircuitBuilder** agent to design the wiring and verify behaviour.

### Debug a signal problem

Use **sim-diagnosis** skill: backtrace sources, forwardtrace consumers,
inspect wire values across ticks.

## References

- **Manual:** https://ifetch.rocks/manual/
- **RE tools API:** `src/ifetchrocks_sim/re_tools.py`
- **Testing API:** `src/ifetchrocks_sim/testing/` — CircuitBuilder, device test helpers
- **Parent project:** https://github.com/securitycopper/i-fetch-rocks (CPU, game save programmer)

## If unclear

When in doubt, use **sim-diagnosis** skill to inspect the simulator state
or **CircuitBuilder** to isolate a device in a minimal test.
