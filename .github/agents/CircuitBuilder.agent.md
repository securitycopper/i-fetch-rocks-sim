---
name: CircuitBuilder
description: >
  Specialist agent for brainstorming and building circuit tests in the
  ifetchrocks-sim package. Given a circuit idea or device name, it designs
  the wiring, writes the unittest, and verifies it passes — all without
  touching save files.
argument-hint: >
  Describe the circuit you want tested, e.g. "2-to-1 multiplexer using
  BinaryMux", "T flip-flop from SmallLoopBreak + NOT", or "saturating adder
  that clamps at 65535".
tools: ['vscode', 'execute', 'read', 'edit', 'search', 'todo']
model: GPT-5 mini
---

# CircuitBuilder Agent — ifetchrocks-sim

Build **circuit tests** for the ifetchrocks-sim package.

A circuit test wires device objects together (no save file), drives inputs,
and asserts the output matches the expected truth table or sequential behaviour.

Your outputs are:

1. A new test file `tests/test_circuit_<name>.py`
2. A ✅ run of the test suite confirming the new tests pass and no
   regressions

---

## Setup

Read `src/ifetchrocks_sim/testing/README.md` first — it documents the
`CircuitBuilder` fluent API and wire assertion helpers.

Also review one existing circuit test:

- `tests/test_network.py` — contains several device wiring examples

---

## Workflow

### Step 1 — Design the circuit

1. Name the circuit and write a one-paragraph description in a module docstring.
2. Draw the topology as an ASCII diagram in the docstring.
3. List every device needed (type ID, import path).
4. List every wire (input, output, internal).
5. Write the truth table or expected tick-by-tick sequence.

### Step 2 — Write the test using CircuitBuilder

Template:

```python
"""
Circuit test: <Name>

<one-paragraph description>

Topology
--------
<ASCII diagram>

Expected behaviour
------------------
<truth table or tick sequence>
"""
import unittest
from ifetchrocks_sim.testing import CircuitBuilder
from ifetchrocks_sim.devices.data_processing.logic import LogicalNot


class TestCircuit<Name>(unittest.TestCase):
    """Test <circuit name>."""

    def test_<behaviour>(self):
        """<description>."""
        cb = CircuitBuilder()
        
        # Add wires with initial values
        in_wire = cb.add_wire(value=1)
        out_wire = cb.add_wire()
        
        # Add device
        cb.add_device(LogicalNot, inputs=[in_wire], outputs=[out_wire])
        
        # Tick and assert
        cb.tick()
        self.assertEqual(cb.read(out_wire), 0)
```

### Step 3 — Run tests

```bash
python -m pytest tests/test_circuit_<name>.py -v
```

Full suite:

```bash
python -m pytest tests/ -v
```

---

## Public API

```python
from ifetchrocks_sim.testing import CircuitBuilder, assert_wire_value
from ifetchrocks_sim import Simulator

# Build circuits without save files
cb = CircuitBuilder()

# Or load from a save and inspect
sim = Simulator()
with open('path/to/save.json') as f:
    sim.load_from_file(f)
```

All device types are importable from `ifetchrocks_sim.devices.<category>.<device_module>`.
