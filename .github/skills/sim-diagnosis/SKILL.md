---
name: sim-diagnosis
description: "Diagnose signal propagation problems in ifetchrocks-sim. Use when: a wire stays 0, a register never latches, a device output is dead, or you need to understand why a circuit isn't working. Keywords: backtrace, forwardtrace, signal analysis, wire tracing, dead signal, stuck register, circuit diagnosis."
argument-hint: "Describe the symptom, e.g. 'output wire never changes' or 'register latch fails to update'"
---

# Simulator Diagnosis — Tool Catalog

Catalog of ifetchrocks-sim tools for diagnosing signal propagation issues.

All examples assume a loaded simulator:

```python
from ifetchrocks_sim import Simulator

sim = Simulator()
with open('path/to/save.json') as f:
    sim.load_from_file(f)
```

---

## 1. Find a wire by prefix

The quickest way to get a full wire UUID:

```python
network = sim.find_network('a1b2c3d4')  # short prefix
if network:
    full_uuid = list(network.nodes.keys())[0]
    print(f"Full UUID: {full_uuid}")
else:
    print("No network found for that prefix")
```

---

## 2. Read a wire's current value

```python
network = sim.find_network('a1b2c3d4')
wire_uuid = 'a1b2c3d4-full-uuid-here'
value = network.get_value(wire_uuid)
print(f"Current value: {value}")
```

For large (vector) networks:

```python
large_net = sim.find_network('vec-prefix')
values = large_net.get_value('vec-uuid')
print(f"Vector [16]: {values}")
```

---

## 3. Backtrace — Who drives this wire?

Find the source device(s) feeding a wire:

```python
sim.print_backtrace('a1b2c3d4', max_depth=10)
```

Returns a tree showing:
- Source device and output port
- Intermediate devices (splitters, mergers, conduits)
- Connection chain down to the target wire

**Flags to watch for:**
- `[LOOP_BREAK]` — SmallLoopBreak or LargeLoopBreak; signal is latched
- `[UNKNOWN]` — UnknownDevice in path (unimplemented device type)
- `[CYCLE]` — circular dependency detected
- `[MAX_DEPTH]` — traversal limit reached; increase `max_depth` or simplify circuit

### Example output

```
Backtrace of a1b2c3d4
  ← BinaryAnd (port 'output')
      ← FourBitSwitch (port 'output')
      ← BinaryOr (port 'output')
          ← Register (port 'output') [LOOP_BREAK leaf]
```

Interpretation: the wire is output by BinaryAnd, which reads from a switch and 
an OR gate. The OR gate's output comes from a register (latched, so backtrace stops).

---

## 4. Forwardtrace — What consumes this wire?

Find all devices that read from a wire:

```python
sim.print_forwardtrace('a1b2c3d4', max_depth=10)
```

Returns a tree showing:
- Devices that directly read this wire
- Their output ports (what they compute)
- Devices that consume those outputs

### Example output

```
Forwardtrace of a1b2c3d4
  → BinaryMux (port 'control')
      → BinaryAnd (port 'a')
          → ValueDisplay (port 'input')
  → Register (port 'data_in')
      → Backtrace from Register output (use backtrace for downstream)
```

Interpretation: this wire feeds the mux control input, which drives an AND gate 
that powers a display. It also feeds a register's data input.

---

## 5. Capture wire values over multiple ticks

Record what a wire does across N ticks:

```python
from ifetchrocks_sim import Simulator

sim = Simulator()
with open('save.json') as f:
    sim.load_from_file(f)

network = sim.find_network('wire-prefix')
wire_uuid = 'full-wire-uuid'

values = []
for tick in range(20):
    sim.tick()
    val = network.get_value(wire_uuid)
    values.append((tick, val))

print("Tick | Value")
for tick, val in values:
    print(f"{tick:4d} | {val}")
```

**Patterns to look for:**
- All zeros → wire is dead
- Same value throughout → latched or constant
- Regular transitions → working correctly
- Unexpected jumps → multiple sources or timing bug

---

## 6. Device introspection

List all devices in a loaded save:

```python
for room_name, devices in sim.found_devices.items():
    print(f"\n{room_name}:")
    for dev in devices:
        print(f"  {dev.name:30s} (uuid={str(dev.uuid)[:8]})")
```

Find devices by type:

```python
from ifetchrocks_sim.devices.data_processing.logic import LogicalNot

not_gates = [d for devs in sim.found_devices.values() 
             for d in devs 
             if isinstance(d, LogicalNot)]
print(f"Found {len(not_gates)} NOT gates")
```

---

## 7. Circuit testing without save files

Use CircuitBuilder to test a suspect device in isolation:

```python
from ifetchrocks_sim.testing import CircuitBuilder
from ifetchrocks_sim.devices.data_processing.logic import LogicalNot

# Build minimal circuit
cb = CircuitBuilder()
in_wire = cb.add_wire(value=1)
out_wire = cb.add_wire()
cb.add_device(LogicalNot, inputs=[in_wire], outputs=[out_wire])

# Tick
cb.tick()

# Check output
assert cb.read(out_wire) == 0, "NOT gate failed!"
print("✓ NOT gate works")
```

This isolates the device behavior from complex save-file wiring and timing.

---

## 8. Common symptoms and remedies

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| Wire stuck at 0 | No source or source is broken | `print_backtrace()` |
| Wire never updates | Latched behind LOOP_BREAK | Trace the latch input |
| Device output wrong | Inputs not matching expectation | `print_backtrace()` for inputs |
| Register doesn't latch | Write-enable stuck low or clock off | Backtrace WE and clock signals |
| Splitter output is 0 | Input stuck 0 or splitter unimplemented | Check input, test device in isolation |

---

## 9. Save & restore simulator state

Save the state after a bad tick, restore to debug more:

```python
import pickle

# Run to tick 100
sim = Simulator()
with open('save.json') as f:
    sim.load_from_file(f)
for _ in range(100):
    sim.tick()

# Save state
state_snapshot = pickle.dumps(sim)

# Later, restore and resume
sim = pickle.loads(state_snapshot)
sim.tick()  # Now at tick 101
```

---

## Full API reference

```python
from ifetchrocks_sim import Simulator

sim.load_from_file(f)
sim.tick()
sim.find_network(wire_prefix)
sim.backtrace_ancestors(wire_prefix)
sim.forwardtrace_consumers(wire_prefix)
sim.print_backtrace(wire_prefix)
sim.print_forwardtrace(wire_prefix)
sim.found_devices  # dict[room_name: str, devices: list[Device]]
```

See `src/ifetchrocks_sim/simulator.py` for the full `Simulator` API.
