# testing

Test helpers for building and asserting simulator circuits in unit tests.

## Modules

| Module | Class / helper | Description |
|---|---|---|
| `circuit_builder.py` | `CircuitBuilder` | Fluent builder for assembling small in-memory device graphs without a save file. Construct devices, wire them together, and tick the circuit in a few lines. |
| `wire_assertions.py` | `assert_wire_value`, `assert_wire_sequence` | `unittest`-style assertion helpers that report the full wire context on failure. |

## Quick example

```python
from ifetchrocks_sim.testing import CircuitBuilder
from ifetchrocks_sim.devices.data_processing.logic.logical_not import LogicalNot

def test_not_gate_inverts():
    cb = CircuitBuilder()
    in_wire  = cb.add_wire(value=1)
    out_wire = cb.add_wire()
    cb.add_device(LogicalNot, inputs=[in_wire], outputs=[out_wire])
    cb.tick()
    assert cb.read(out_wire) == 0
```
