# ifetchrocks-sim — Agents & Skills

This directory contains specialized agents and skills for developing the
**ifetchrocks-sim** package.

## Agents

### 🔧 DeviceRE
Reverse-engineer new device implementations for the simulator.

**When to use:** You've placed a new device type in the Engine Room RE save,
wired it to probes, and saved the game. DeviceRE reads the save, identifies
port IDs, and guides you through implementation.

**Invoke:** `DeviceRE.agent.md`

### ⚡ CircuitBuilder
Design and test circuits without a save file.

**When to use:** You want to test a device behavior in isolation, or design
a multi-device circuit (e.g., counter, latch, mux) and verify it works before
wiring it in-game.

**Invoke:** `CircuitBuilder.agent.md`

---

## Skills

### 🔍 device-setup
Interactive reverse-engineering skill for identifying device ports.

Paired with DeviceRE — this skill handles the detailed port-ID extraction
after the device is placed and wired in-game.

### 🧪 sim-diagnosis
Diagnose signal propagation problems in loaded saves or test circuits.

**When to use:** A wire stays at 0, a register won't latch, a device output
is dead, or a circuit behaves unexpectedly.

**Tools:** backtrace (find sources), forwardtrace (find consumers), wire value
inspection, device introspection.

---

## Public APIs used

All agents and skills use the **public ifetchrocks-sim API**:

```python
from ifetchrocks_sim import Simulator
from ifetchrocks_sim.re_tools import RESave
from ifetchrocks_sim.testing import CircuitBuilder
```

No private paths; safe for external users and contributors.

---

## References

- **RE save:** `game_app_data/Saves/102d6094-bff6-413a-b859-b4992647c9e5.json`
- **RE tools API:** `src/ifetchrocks_sim/re_tools.py`
- **Testing API:** `src/ifetchrocks_sim/testing/`
- **Devices:** `src/ifetchrocks_sim/devices/`
