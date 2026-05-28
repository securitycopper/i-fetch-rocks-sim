# Reverse-Engineering Device Port IDs

This guide explains how to infer the `indexedChildren` key → port-name mapping
for any unknown in-game component using a controlled save-file probe.

---

## Background

Every wired connection in the game is stored as a **shared wire UUID**.  
Two devices that are wired together each carry a child node whose `uuid` field
is identical.  The `indexedChildren` dict is keyed by an integer-as-string
**port key** that is stable across all saves for the same component type.

```
Device A                     Device B
indexedChildren:             indexedChildren:
  "1234567": { uuid: "abc" }   "9876543": { uuid: "abc" }
                     ^^^^^^^^^^^^^^^^^^
                     same UUID → they are connected
```

So to name a port you need to:
1. **Know what is on the other end** of the wire (the probe device).
2. **Know which port on the probe device** carries that wire.
3. **Look up the port key on the device under test** that shares the UUID.

---

## Choosing Probe Components

The best probes have exactly **one** data wire — their connection is unambiguous:

| Probe | Type ID | Simulator class | Output/input key | Notes |
|---|---|---|---|---|
| `FourBitSwitch` | 42 | `FourBitSwitch` | single child (`indexedChildren` has 1 entry) | Use stored value 0 / 65535 to tell apart visually |
| `ControllerDial` | 78 | `ControllerDial` | single child | Dial value is in `indexedDeviceData` |
| `SwitchSingle` | 202 | `SwitchSingle` | single child | Binary 0/1; use for WRITE/trigger ports |
| `ValueDisplay` | 71 | `ValueDisplay` | input key `-923971752` (confirmed) | Connects to ports that drive a readable value |
| `BinaryLightArray` | 122 | `BinaryLightArray` | input key `832364048` (confirmed) | Good for 16-bit output ports |

**Rule of thumb:**
- Use `SwitchSingle` (or a `FourBitSwitch` toggled 0/65535) for boolean trigger
  inputs (e.g. WRITE).
- Use `FourBitSwitch` with distinct stored values (e.g. 1, 2, 4, 8) for
  multi-bit data inputs — the value tells you which toggle maps to which port.
- Use `ValueDisplay` or `BinaryLightArray` for output ports.

---

## Resolving Ambiguity Between Multiple Inputs

When several inputs have the same probe type, use **room-child ordering** to
distinguish them.  The game stores `indexedChildren` in creation order.  Proof:

```
In save 102d6094 (2026-03-20) the room node had children in this order:
  room_child_key=1572498934  type=42  uuid=f7ba5b07  stored=0       -> toggle 0
  room_child_key=-972184717  type=42  uuid=336c032a  stored=65535   -> toggle 1
  room_child_key=-1865877987 type=42  uuid=17cfb76f  stored=0       -> toggle 2
  room_child_key=628589608   type=42  uuid=d5ca7895  stored=65535   -> toggle 3
```

Since the FourBitSwitch toggles are placed in the room **in the order they were
placed**, toggling them in a predictable sequence and reading the room list back
gives you the `toggle index → save-file uuid → bay port key` chain.

Alternatively, set **distinct stored values** (e.g. 100, 200, 300, 400) on the
dials before saving.  The `signalValue` or `indexedDeviceData` field on each
probe will let you match without relying on ordering.

---

## Step-by-Step Wiring Procedure

### 1 — Prepare the save

In-game, place the **target device** plus one probe per port in the same room.
Wire each probe to exactly one port on the target.  Good layout:

```
FourBitSwitch(toggle 0, stored=1)   ──→  target ?port_A
FourBitSwitch(toggle 1, stored=2)   ──→  target ?port_B
FourBitSwitch(toggle 2, stored=4)   ──→  target ?port_C
SwitchSingle (stored=0)             ──→  target ?port_trigger
                       target ?port_out ──→  ValueDisplay
                       target power_in  ──→  SmallPowerSplitter
```

Save the game, note the filename.

### 2 — Read the port map

```python
import json

with open('game_app_data/Saves/<uuid>.json', encoding='utf-8') as f:
    data = json.load(f)

by_uuid = {}
def walk(node):
    if isinstance(node, dict):
        if 'uuid' in node: by_uuid[node['uuid']] = node
        for v in node.values(): walk(v)
    elif isinstance(node, list):
        for v in node: walk(v)
walk(data)

# Find target device by type
target = next(n for n in by_uuid.values() if n.get('type') == <TARGET_TYPE_ID>)

# Build: wire_uuid -> [(owner_uuid, port_key, owner_type)]
wire_owners = {}
for dev_uuid, dev in by_uuid.items():
    for ck, cc in (dev.get('indexedChildren') or {}).items():
        if isinstance(cc, dict) and 'uuid' in cc:
            wire_owners.setdefault(cc['uuid'], []).append((dev_uuid, ck, dev.get('type')))

# Print each port of the target and what connects to it
for port_key, child in (target.get('indexedChildren') or {}).items():
    wire_uuid = child.get('uuid', '')
    others = [x for x in wire_owners.get(wire_uuid, []) if x[0] != target['uuid']]
    probe_str = ', '.join('type=%s uuid=%s key=%s' % o for o in others)
    print('target port_key=%-15s child_type=%s  -> %s' % (
        port_key, child.get('type'), probe_str or '[no other end]'))
```

### 3 — Identify each port

Cross-reference probe stored values:

```python
# For each probe FourBitSwitch that appears in the output above:
for dev_uuid, dev in by_uuid.items():
    if dev.get('type') == 42:
        vals = list((dev.get('indexedDeviceData') or {}).values())
        stored = vals[0]['signal'] if vals else '?'
        print('FBS uuid=%s  stored=%s' % (dev_uuid[:8], stored))
```

- The target port whose other end is the FBS with **stored=1** → semantic input A  
- stored=2 → input B, stored=4 → input C, etc.
- The port connected to `ValueDisplay` (type 71) → output port
- The port connected to `SwitchSingle` (type 202) → trigger/write port
- The port with a type-3 child (and other end is a power splitter) → power input

### 4 — Look up the device type ID

Use the type census script if the type ID is unknown:

```python
from collections import Counter
type_counts = Counter(n.get('type') for n in by_uuid.values())
print(type_counts.most_common(30))
```

Compare against `ComponentType` in `simulator.py`.  If the type ID is absent
it is new — check `docs/manual/index.md` to find the device name.

---

## Structural Patterns

### Type changes when a drive is inserted

Memory Bay with no drive = type **141**.  
Memory Bay with Drive A inserted = type **153**.  
The port keys change between the two states; always probe with a drive inserted.

### Power ports

Power inputs use type-3 (small) or type-2 (large) wire children.  They appear
in `indexedChildren` like data wires.  The confirmed key for the bay power port
is `1096989087`.  Power ports do not need simulation logic but should be listed
in `input_power_networks` for the graph visualiser.

### Drive-slot children

Type-139 children are Drive A slots.  They appear in the parent's
`indexedChildren` — record the key as `DRIVE_A_SLOT` for future DriveA linkage.

---

## Confirmed Port-Key Reference

### MemoryBaySignal / MEMORY_BAY_WITH_DRIVE_A (type 153)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-20.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_INPUT` | `-723312417` | Data to write | FourBitSwitch toggle 0 |
| `PORT_W_INDEX` | `937671010` | Write address 0–65535 | FourBitSwitch toggle 1 |
| `PORT_WRITE` | `1266942261` | Write trigger (nonzero=write) | FourBitSwitch toggle 2 |
| `PORT_O_INDEX` | `-1305286718` | Read address 0–65535 | FourBitSwitch toggle 3 |
| `PORT_OUTPUT` | `1892577010` | drive[O-Index] output | BinaryLightArray |
| `DRIVE_A_SLOT` | `-606208362` | type-139 Drive A child | type inspection |
| `POWER_PORT` | `1096989087` | Power input | type-3 wire to SmallPowerSplitter |

Address range: 0–65535 (full 16-bit; manual is outdated, cap was raised in a recent update).

### EightBitSwitch / SWITCH_BANK_LONG (type 40)

Source: in-game probe, 2026-03-22. All 8 bits confirmed individually via single-switch → ValueDisplay.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_OUTPUT` | `1420098671` | 0–255 output | ValueDisplay (all probes) |
| bit 128 key | `1718803965` | toggle 128 | switch 128 only → output 128 |
| bit 64 key | `-49703703` | toggle 64 | switch 64 only → output 64 |
| bit 32 key | `1509656464` | toggle 32 | switch 32 only → output 32 |
| bit 16 key | `-120397473` | toggle 16 | switch 16 only → output 16 |
| bit 8 key | `1085911864` | toggle 8 | switch 8 only → output 8 |
| bit 4 key | `716941455` | toggle 4 | switch 4 only → output 4 |
| bit 2 key | `692338407` | toggle 2 | switch 2 only → output 2 |
| bit 1 key | `55203747` | toggle 1 | switch 1 only → output 1 |

State encoding: `rotation.y < 0` → ON; `rotation.y ≥ 0` → OFF.

---

### LogicalMux (type 134)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_IN_TRUE` | `-1305286718` | Selected when mux>0 | FBS probe A (stored=0), index 0 |
| `PORT_IN_MUX` | `-108496386` | Selector signal | FBS probe C (stored=1), index 1 |
| `PORT_IN_FALSE` | `-1907579157` | Selected when mux==0 | FBS probe B (stored=2), index 2 |
| `PORT_OUT` | `835233603` | Boolean output (0 or 1) | ValueDisplay shows 0 |

Verification: mux=1 (true) → selects in_true=0 → output=0 ✓  
Output is always 0 or 1 regardless of input magnitude (manual confirmed).

---

### OneBitSwitch / BIT_SWITCH_1 (type 215)

Source: RE save `102d6094`, 2026-03-22. Both states confirmed via type=215 → ValueDisplay probe.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_OUTPUT` | `245567209` | 0 or 1 output | ValueDisplay probe |
| toggle key | `-1426717297` | ON/OFF state | OFF rot.y=-0.2588 signal=0; ON rot.y=+0.2588 signal=65535 |

State encoding: `rotation.y > 0` → ON → output 1; `rotation.y ≤ 0` → OFF → output 0.

---

### FourToggleSwitch (type 126)

Source: save `102d6094`, 2026-03-24. All 4 outputs wired to VD_0–VD_3, switches set to 0000.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_OUTPUT_0` | `245567209` | Toggle 0 boolean output | VD_0 = 0 when switch 0 OFF |
| `PORT_OUTPUT_1` | `-524987108` | Toggle 1 boolean output | VD_1 = 0 when switch 1 OFF |
| `PORT_OUTPUT_2` | `1831607210` | Toggle 2 boolean output | VD_2 = 0 when switch 2 OFF |
| `PORT_OUTPUT_3` | `1502427632` | Toggle 3 boolean output | VD_3 = 0 when switch 3 OFF |

State encoding: `rotation.y > 0` → ON → output 65535; `rotation.y ≤ 0` → OFF → output 0.


### SignalInequalities (type 102)

Source: RE save `102d6094`, 2026-03-22. Confirmed via FBS probes (signal=5/8, bounds=3/7) → ValueDisplay.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_SIGNAL` | `1000035408` | signal input | FBS values wired here |
| `PORT_THRESHOLD_A` | `1286147805` | first threshold (symmetric) | FBS value=3 or 7 |
| `PORT_THRESHOLD_B` | `101010795` | second threshold (symmetric) | FBS value=7 or 3 |
| `PORT_OUTPUT` | `-411018612` | boolean out — 65535 if in range else 0 | VD confirmed |

Logic: `output = 65535 if min(a,b) < signal < max(a,b) else 0` (strict, symmetric bounds)

Edge cases confirmed 2026-03-22:
- signal=3, a=3, b=7 → 0 (strict lower)
- signal=7, a=3, b=7 → 0 (strict upper)  
- signal=5, a=7, b=3 → 65535 (symmetric: bounds auto-reordered)

---

### GasSensor (type 44)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_CO` | `375148252` | CO gas % as 16-bit (0–65535) | wired → VD_0 |
| `PORT_O2` | `1560142200` | O2 gas % as 16-bit (0–65535) | wired → VD_1 |
| `PORT_CO2` | `8765768` | CO2 gas % as 16-bit (0–65535) | wired → VD_2 |

No inputs — sensor outputs only. Output values read from in-game atmosphere; all ports always present.

---

### ElementDisplay (type 72)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_INPUT` | `1878156136` | 16-bit signal input (0–65535 → elemental symbol) | wired ← IN_0 |
| `PORT_OUTPUT` | `-1899773318` | passthrough output (same value) | wired → VD_0 |
| `PORT_POWER` | `-1409524763` | power input | child_type=3 wire to LargePowerSplitter |

Manual: "converts a 16-binary value to the two letter elemental symbol from the periodic table."  
Display-only in-sim: output passes the input value through unchanged.

---

### LinearLightArray (type 39)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_INPUT` | `832364048` | 16-bit signal input (0–65535 → % of 40 LEDs lit) | wired ← IN_0 |
| `PORT_OUTPUT` | `-1186727754` | passthrough output (same value) | wired → VD_0 |
| `PORT_POWER` | `-1831826590` | power input | child_type=3 wire to LargePowerSplitter |

Note: `PORT_INPUT` key `832364048` is the same as `BinaryLightArray.PORT_INPUT`.  
Manual: "displays a 16-bit value as a percentage of 40 LEDs — 0=all off, 65535=all 40 on."

---

### LogicalXnorGate (type 29)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_INPUT_A` | `-1305286718` | first input (0=false, >0=true) | wired ← IN_0 |
| `PORT_INPUT_B` | `-108496386` | second input (0=false, >0=true) | wired ← IN_1 |
| `PORT_OUTPUT` | `835233603` | 1 if both same, 0 if different | wired → VD_0 |

Logic: `output = 1 if bool(A) == bool(B) else 0`. Output is always 0 or 1.

---

### BinaryAndGate (type 118)

Source: save `102d6094-bff6-413a-b859-b4992647c9e5`, 2026-03-23.

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_INPUT_A` | `2034020425` | first 16-bit operand | wired ← IN_0 |
| `PORT_INPUT_B` | `1173709222` | second 16-bit operand | wired ← IN_1 |
| `PORT_OUTPUT` | `-1790705161` | bitwise AND result (16-bit) | wired → VD_0 |

Note: all three port keys are identical to `BinaryOrGate` and `BinaryXorGate`.  
Logic: `output = (A & B) & 0xFFFF`.

---

### FourButtonBank (type 47)

Source: save `102d6094`, 2026-03-24. All 4 outputs wired to VD_0–VD_3, all buttons released (0000).

| Constant | Key | Semantic | How confirmed |
|---|---|---|---|
| `PORT_OUTPUT_0` | `508190823` | Button 0 (rightmost) output | VD_0 = 0 when released |
| `PORT_OUTPUT_1` | `-1550188168` | Button 1 output | VD_1 = 0 when released |
| `PORT_OUTPUT_2` | `-703635148` | Button 2 output | VD_2 = 0 when released |
| `PORT_OUTPUT_3` | `-1135664085` | Button 3 (leftmost) output | VD_3 = 0 when released |

Physical order left→right: button 3 (VD_3) … button 0 (VD_0).  
Momentary: output 65535 when held, 0 when released. No rotation encoding in IDD.

---

## Implementation Pattern

After port IDs are confirmed, the component implementation follows the
**Register** pattern in
`code/ifetchrocks/sim/devices/data_processing/memory/register.py`:

```python
from ifetchrocks.sim.data_network.DataNetworkManager import DataNetworkManager
from ifetchrocks.sim.devices.utils.device_utils import get_connection_uuid_by_id

class MyDevice:
    PORT_IN  = '<confirmed_key>'
    PORT_OUT = '<confirmed_key>'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.network_in  = get_connection_uuid_by_id(data, self.PORT_IN)
        self.network_out = get_connection_uuid_by_id(data, self.PORT_OUT)

        self.input_networks  = [self.network_in]
        self.output_networks = [self.network_out]

        if self.network_in:
            network_manager.get_network(self.network_in).register_listener(self._on_in)

    def _on_in(self, uuid: str, value: int):
        self._value = value & 0xFFFF
        self.update_and_notify()

    def update_and_notify(self):
        self.network_manager.get_network(self.network_out).update_source(
            self.uuid, self._value)
```

**Checklist for a complete implementation:**
1. `input_networks` lists every data input wire UUID (None-safe for optional ports)
2. `output_networks` lists every data output wire UUID
3. `input_power_networks` lists every power input wire UUID (if applicable)
4. All output wire updates go through `update_source(self.uuid, value)` on the
   correct `DataNetwork`
5. All arithmetic results masked to `0xFFFF` before going onto a wire

---

## Registration

After implementing, register in `simulator.py`:

```python
# 1. ComponentType enum — add the type ID
MEMORY_BAY_WITH_DRIVE_A = 153

# 2. DeviceClasses enum — map the name to the class
MEMORY_BAY_WITH_DRIVE_A = MemoryBaySignal
```

Both names must match exactly (Python `Enum` lookup uses the name string).

---

## Testing

After implementation, write unit tests under
`test/ifetchrocks/sim/devices/Test<DeviceName>.py`.
Use `_make_<device>()` helpers that build the `data` dict directly with the
confirmed port-key constants from the device class — **never hardcode raw key
strings in tests**.

For behavioural/functional tests that verify the device works inside a real
circuit, delegate to the **CircuitBuilder** agent with the circuit description.

Minimum test coverage:
- Default output (fresh device, no inputs driven)
- Each input independently updates the correct internal state
- Output updates when output-triggering inputs change
- Trigger/write gating (output not updated when trigger is 0, if applicable)
- 16-bit value masking on all inputs and outputs
- Partial wiring (only output wired) does not raise

See `test/ifetchrocks/sim/devices/TestMemoryBaySignal.py` for a worked example.
