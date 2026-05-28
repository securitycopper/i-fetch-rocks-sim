# Unknown Wired Devices — Ship CPU Save (`d88a1650`)

Census date: 2026-03-31. Save: `game_app_data/Saves/d88a1650-10b4-4d00-8c31-f69b4b41dee2.json`.

## Progress

| Scope | Done | Total | % |
|-------|------|-------|---|
| Ship CPU wired types (this table) | 8 | 16 | 50% |
| Manual device entries (below) | 13 | 42 | 31% |
| **Overall** | **21** | **58** | **36%** |

Types with zero wired ports (cosmetic/passive) are excluded. All DONE types removed — see git log for confirmed port IDs.

| Type ID | Count in CPU | IC ports | Cross-save count | Likely identity | Status |
|---------|-------------|----------|-----------------|-----------------|--------|
| 147 | 2 | 3 data | 1 | Vector memory bay variant | TODO |
| 146 | 2 | 3 data | 44 | Vector memory bay variant | TODO |
| 220 | 2 | 2 data | 1 | Unknown | TODO |
| 167 | 2 | 1 data | 85 | Unknown single-port | TODO |
| 120 | 1 | 3 data | 25 | **`BINARY_XOR`** — confirmed via neighbor direction analysis 2026-03-29; port keys match AND/OR; registered as type 120 | DONE |
| 211 | 1 | 2 data | 3 | Unknown | TODO |
| 145 | 1 | 3 data | 1 | Unknown | TODO |

---

## Unknown Room Connections

**Moved to [`docs/room-port-map.md`](room-port-map.md)** — full roomRE with all
rooms, all large-cable wall sockets, direction analysis, cross-room pairing
hypotheses, and simulator fix plan. See that document for current status.

---

## Remaining unimplemented manual devices

Cross-reference of `docs/manual/index.md` vs `DeviceClasses` enum in `simulator.py`. Type IDs marked `?` are not yet reverse-engineered.

### Power distribution

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/POWER_DISTRIBUTION/ENERGY_CELLS/LARGE_CELL` | `DeviceLargeEnegryCell.md` | ? | — |
| `/POWER_DISTRIBUTION/ENERGY_CELLS/SHIELDED_SMALL_CELL` | `HighCapacitySmallEnergyCell.md` | ? | — |
| `/POWER_DISTRIBUTION/ENERGY_CELLS/SHIELDED_LARGE_CELL` | `HighCapacityLargeEnergyCell.md` | ? | — |
| `/POWER_DISTRIBUTION/REDUNDANT/SMALL_REDUNDANT` | `SmallRedundantPower.md` | ? | — |
| `/POWER_DISTRIBUTION/REDUNDANT/LARGE_REDUNDANT` | `LargeRedundantPower.md` | ? | — |

### Controllers

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/CONTROLLERS/JOYSTICKS/2_AXIS_RESTRICTED_JOYSTICK` | `Device2dJoystickConstrained.md` | ? | Constrained 2-axis variant |
| `/CONTROLLERS/JOYSTICKS/REALITY_JOYSTICK` | `RealJoystickController.md` | ? | Maps real physical joystick input |

### Data distribution

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_DISTRIBUTION/DATA_SPLITTERS/VECTOR_SIGNAL_SPLITTER` | `VectorSplitter.md` | ? | Splits 16-element vector signal |
| `/DATA_DISTRIBUTION/DATA_MERGERS/MULTIPLEX_MERGER` | `DeviceSmallLargeCableMerger.md` | ? | Compact multiplex merger |
| `/DATA_DISTRIBUTION/DATA_MERGERS/VECTOR_MERGER` | `VectorPacker.md` | ? | Packs scalars into vector |

### Data processing — math

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_PROCESSING/MATH/SCOPED/TRIGGERED` | `DeviceTriggeredSignal.md` | ? | Gated/triggered signal passthrough |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_MAGNITUDE` | `VectorMagnitude.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_ADD` | `VectorAdd.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_MINUS` | `VectorMinus.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_MULTIPLY` | `VectorMultiply.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_DIVIDE` | `VectorDivide.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_DOT` | `DeviceVectorDot.md` | ? | |
| `/DATA_PROCESSING/MATH/VECTOR_ARITHMETIC/VECTOR_CROSS` | `DeviceVectorCross.md` | ? | |

### Data processing — logic

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_PROCESSING/LOGIC/NAND_GATE` | `DeviceLogicalNAND.md` | 27 | DONE — `LogicalNandGate`; type 27 RE-confirmed 2026-03-22; registered in `ComponentType` 2026-03-29 |
| `/DATA_PROCESSING/LOGIC/XOR_GATE` | `DeviceLogicalXOR.md` | **28** (inferred) | Sequential gap: 24=OR, 25=AND, 26=NOR, 27=NAND, **28=?**, 29=XNOR. All 5 save instances are inventory-only (zero ports, loc=0) — no wired example to confirm. Needs in-game RE before registering. |

> **BOOLEAN_LIGHT (type=214) port structure confirmed 2026-03-29** (from `d88a1650` instances `56534fcc`, `903b788e`):
> `2000747480`=power, `-1831826590`=power, `373576006`=data-in, `-1186727754`=data-out.
> Current `BooleanLight` impl only has 1 data + 1 wrong power port key (`-1270701682`) — needs fix.
> `LogicalXorGate` test was written against these same keys treating them as data wires — that test's wire typing is inconsistent with save data.

### Data processing — memory / drives

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_PROCESSING/MEMORY/DRIVES/A_DRIVE` | `MemDiskA.md` | 139 | `DriveCartridge` (passive child of MemoryBaySignal bay `326005b1`); microcode ROM |
| `/DATA_PROCESSING/MEMORY/DRIVES/B_DRIVE` | `MemDiskB.md` | 156 | `DriveCartridge` (passive child of MemoryBaySignal bay `1882395a`); ALU signals ROM |
| `/DATA_PROCESSING/MEMORY/DRIVES/C_DRIVE` | `MemDiskC.md` | 157 | `DriveCartridge` (passive child of MemoryBaySignal bay `ff834c44`); program ROM |
| `/DATA_PROCESSING/MEMORY/DRIVES/D_DRIVE` | `MemDiskD.md` | 158 | `DriveCartridge` (passive); IDD write-switch key `1376775829` |
| `/DATA_PROCESSING/MEMORY/DRIVES/E_DRIVE` | `MemDiskE.md` | 159 | `DriveCartridge` (passive); type RE-confirmed 2026-03-24 |
| `/DATA_PROCESSING/MEMORY/MEMORY_BAY_VECTOR` | `MemoryBayVector.md` | 143 / 154 | DONE — type 154 (loaded) and 143 (empty) both map to `MemoryBayVector`; 22 tests passing |
| `/DATA_DISTRIBUTION/DATA_SPLITTERS/VECTOR_MULTIPLEX_SPLITTER` | `PacketVectorSplitter.md` | 149 | DONE — `PacketVectorSplitter`; 7 tests passing (2026-03-26) |
| `/DATA_DISTRIBUTION/DATA_MERGERS/VECTOR_MULTIPLEX_MERGER` | `PacketVectorMerger.md` | 150 | DONE — `PacketVectorMerger`; 7 tests passing (2026-03-26) |

### Data processing — sensors

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_PROCESSING/SENSORS/PROXIMITY_SENSOR` | `DeviceProximitySensor.md` | ? | — |
| `/DATA_PROCESSING/SENSORS/SHIP_VECTORS` | `ShipVectors.md` | ? | Outputs ship velocity/heading vectors |

### Data processing — generators

| Manual path | Manual file | Type ID | Notes |
|-------------|-------------|---------|-------|
| `/DATA_PROCESSING/GENERATORS/SINE_WAVE` | `DeviceSine.md` | ? | Configurable sine oscillator |

---

## Unresolved TODO items in implemented devices

These are devices that **have** a Python class but contain unverified logic or
port mappings flagged with TODO comments. DeviceRE should verify each item
against save data or in-game testing and clear the TODO once confirmed.

| # | Device | File | TODO | Action needed |
|---|--------|------|------|---------------|
| TD-1 | BinaryShift (123) | `sim/devices/data_processing/binary/binary_shift.py` L131 | `check this swich` — shift direction switch may be inverted | Verify shift direction with circuit test: input=0x00FF, shift=4 → expected left=0x0FF0, right=0x000F. Compare against manual `DeviceBinaryShiftLong.md`. |
| TD-2 | BinaryShift (123) | `sim/devices/data_processing/binary/binary_shift.py` L158 | `This may be reversied` — shift result may be bit-reversed | Same circuit test as TD-1; confirm output bit ordering. |
| TD-3 | FlightSplitter (50) | `sim/devices/data_distribution/data_splitters/flight_splitter.py` L17 | Channel index→port-key mapping is placeholder | Load save with FlightSplitter instances, trace which port outputs which vector channel. Update `_SMALL_OUTPUT_PORT_KEYS` ordering. |
| TD-4 | ChannelSplitter (62) | `sim/devices/data_distribution/data_splitters/channel_splitter.py` L42 | `Not tested` — bounds check logic unverified | Write circuit test: 32-element vector input, various offset values → verify correct element extracted. |
| TD-5 | LargePowerSplitter (12) | `sim/devices/power_distribution/power_splitters/large_power_splitter.py` L28 | Missing large output 6 port key | Find `LargePowerSplitter` instances in career save with 7+ children; extract the 7th port key. |
| TD-6 | LongPowerSplitter (63) | `sim/devices/power_distribution/power_splitters/long_power_splitter.py` L155 | Small outputs may be reversed | Trace power distribution in career save from LongPowerSplitter outputs to downstream devices; confirm ordering. |
| TD-7 | SmallPowerSplitter (23) | `sim/devices/power_distribution/power_splitters/small_power_splitter.py` L147 | Output order may not be correct | Same technique as TD-6; verify small output port ordering against save wiring. |
| TD-8 | WirelessReceiver (213) | `sim/devices/data_distribution/wireless/wireless_receiver.py` L39 | Port keys unconfirmed — no wired instance found in any save | Find a save with wired WirelessReceiver instances, or build test circuit in-game. Extract port keys from `indexedChildren`. |
| TD-9 | LargeConduitStub (70) | `sim/devices/data_distribution/data_conduits/large_conduit_stub.py` | Complete no-op stub — zero ports observed in all tested saves | Check newer saves for type 70 with active ports. If still inert, mark as confirmed-inert and remove TODO status. |
