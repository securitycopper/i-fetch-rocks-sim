# ifetchrocks-sim Documentation

## Reverse-Engineering (RE) Guides

This directory contains guides and inventory for reverse-engineering devices in the I Fetch Rocks simulator.

### Core Reference Docs

- **[reverse-engineering.md](reverse-engineering.md)** — **START HERE** for device RE methodology
  - How to identify ports using probe devices
  - Probe selection guide (FourBitSwitch, ValueDisplay, etc.)
  - Port key mapping workflow
  - Best practices for wiring test circuits

- **[re-probe-setup.md](re-probe-setup.md)** — Fixed probe inventory
  - Engine Room probe catalog (IN_0–IN_15, VD_0–VD_15)
  - Probe wire UUID reference
  - Protocol for adding extended probes
  - *Used by DeviceRE agent for all RE sessions*

### Inventory & Progress

- **[unknown-devices-ship-cpu.md](unknown-devices-ship-cpu.md)** — Device RE progress tracker
  - Which device types have been implemented (DONE)
  - Which device types are still TODO
  - Ship CPU vs cross-save counts
  - Unknown room connections status
  - *Update this file as new devices are reverse-engineered and implemented*

### Architecture Reference

- **[ship-topology.md](ship-topology.md)** — Physical ship layout diagram
  - Room layout and coordinates
  - Power distribution overview
  - Useful for understanding which rooms connect to which

- **[room-port-map.md](room-port-map.md)** — Inter-room cable connections
  - Large-cable wall socket inventory by room
  - Cable direction analysis (IN vs OUT)
  - Cross-room wiring topology
  - *Used by room-mapping skill for room connection RE*

---

## Using These Docs with DeviceRE

When using the **DeviceRE** agent or **device-setup** skill:

1. Read [reverse-engineering.md](reverse-engineering.md) to understand the methodology
2. Consult [re-probe-setup.md](re-probe-setup.md) for the probe wire UUIDs
3. Place your device in the Engine Room, wire to probes, save
4. Agent will match ports and guide you through implementation
5. After implementing, update [unknown-devices-ship-cpu.md](unknown-devices-ship-cpu.md) with your findings

---

## Temporal vs Permanent

**Permanent (in this repo):**
- RE methodology & probe protocol
- Device progress inventory
- Architecture reference

**Temporary (in i-fetch-rocks):**
- Intermediate probe scripts (`_tmp_*.py`, `_probe_*.py`)
- Diagnostic traces
- CPU-specific debugging notes (see `docs/cpu-architecture.md`, `docs/microcode-control-signal-map.md` in i-fetch-rocks instead)
