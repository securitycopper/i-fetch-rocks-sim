---
name: DeviceRE
description: >
  Guided reverse-engineering agent for ifetchrocks-sim devices.
  Works through a structured cycle: identify an unimplemented device type,
  help the user wire it up in-game, parse the resulting save file to confirm
  port IDs, implement the simulator device class, register it, and delegate tests to
  CircuitBuilder. Also handles room-connection mapping when the unknown boundary
  is a type-1 room frame rather than a missing device class.
argument-hint: >
  Either "suggest" (pick the best next device to reverse-engineer) or a
  device description, e.g. "type=214 = BooleanLight" or a manual page name
  like "LogicalMux", or a room-connection task such as "room connections",
  "Helm room cable map", or "label Life Support room ports". Device RE uses a
  fixed RE save; room-connection RE uses the active ship save under
  investigation and should not ask the user for a save path.
tools: ['vscode', 'execute', 'read', 'edit', 'search', 'todo', 'agent']
agents: ['CircuitBuilder']
model: Claude Sonnet 4.6 (copilot)
---

# DeviceRE Agent — Reverse-Engineering Workflow

Device reverse-engineering for the **ifetchrocks-sim** package.

## Quick start

1. Run `suggest` mode to see the next best device to reverse-engineer
2. User places device in Engine Room RE save and wires it to probes
3. Agent reads the save, identifies ports, and drives implementation
4. Delegate testing to CircuitBuilder

## Core references

- **RE tools API:** `src/ifetchrocks_sim/re_tools.py` — `RESave`, port matching, probe table
- **Validation:** `src/ifetchrocks_sim/validation.py` — unknown device classification
- **Device base:** `src/ifetchrocks_sim/devices/template.py`
- **Registration:** `src/ifetchrocks_sim/simulator.py` lines ~80 — `ComponentType` enum and device imports

## Save file

- **RE save (always):** `game_app_data/Saves/102d6094-bff6-413a-b859-b4992647c9e5.json`
- Never ask the user for a save path. Always read this save directly.

## Workflow — Mode A (suggest)

1. Analyze known device gaps:
   ```python
   from ifetchrocks_sim.re_tools import RESave
   re = RESave()
   new_devices = re.find_new_devices()  # Compare against baseline
   re.print_new_devices()
   ```

2. Cross-reference unknown type IDs with manual at https://ifetch.rocks/manual/

3. Rank candidates by: impact, complexity, dependencies

4. Instruct user:
   - Place device in Engine Room of RE save
   - Wire inputs to IN_x probes, outputs to VD_x probes
   - Save the game
   - Return to agent

## Workflow — Mode B (implement)

After user saves:

1. Use `re_tools` API to detect new device and match ports to probes:
   ```python
   from ifetchrocks_sim.re_tools import RESave
   re = RESave()
   device_info = re.find_new_devices()[0]  # First new device
   ports = re.port_map(type_id=device_info.type_id)
   re.print_port_map(type_id=device_info.type_id)
   ```

2. Create device implementation:
   - New file: `src/ifetchrocks_sim/devices/<category>/<device_snake_case>.py`
   - Inherit from `Device` base class
   - Define `__init__`, `tick()`, port setup
   - Reference existing device in same category as template

3. Register device:
   - Add import to `src/ifetchrocks_sim/devices/__init__.py`
   - Add to device type enum in `src/ifetchrocks_sim/simulator.py`
   - Verify `get_device` factory sees it

4. Write tests using CircuitBuilder or validation suite

5. Run full test suite:
   ```bash
   python -m pytest tests/ -v
   ```

## Workflow — Mode R (room connections)

Room-connection RE maps port IDs and labels for boundary-crossing cables.
Use for type-1 room frames or when discovering room inlet/outlet ports.

Same probe methodology, but applied to room frame `indexedChildren` ports.
Result: documented port inventory added to `src/ifetchrocks_sim/devices/room.py`.

---

## Public API for sub-agents

CircuitBuilder and other tools call:

```python
from ifetchrocks_sim import Simulator
from ifetchrocks_sim.re_tools import RESave

sim = Simulator()
with open('path/to/save.json') as f:
    sim.load_from_file(f)

re = RESave()
new_devs = re.find_new_devices()
```

No private paths; everything is through public sim API.
