# RE Probe Setup Protocol

The Engine Room of the RE save contains a **fixed, permanent set of probe
devices** — input constants (`IN_0`–`IN_15`, optionally `IN_MAX`) and output
monitors (`VD_0`–`VD_15`). Their wire UUIDs are recorded once in the
DeviceRE agent and treated as constants for all future RE sessions.

**Key rule:** probes never change value. To feed a port a different value,
rewire that port to a different `IN_x` probe. No probe is ever reconfigured.

---

## Probe Inventory (target state)

| Name | Device | Fixed value | Purpose |
|------|--------|-------------|---------|
| `IN_0` | FourBitSwitch | 0 | Logic false / zero |
| `IN_1` | FourBitSwitch | 1 | Logic true / one |
| `IN_2` | FourBitSwitch | 2 | — |
| `IN_3` | FourBitSwitch | 3 | — |
| `IN_4` | FourBitSwitch | 4 | — |
| `IN_5` | FourBitSwitch | 5 | — |
| `IN_6` | FourBitSwitch | 6 | — |
| `IN_7` | FourBitSwitch | 7 | — |
| `IN_8` | FourBitSwitch | 8 | — |
| `IN_9` | FourBitSwitch | 9 | — |
| `IN_10` | FourBitSwitch | 10 | — |
| `IN_11` | FourBitSwitch | 11 | — |
| `IN_12` | FourBitSwitch | 12 | — |
| `IN_13` | FourBitSwitch | 13 | — |
| `IN_14` | FourBitSwitch | 14 | — |
| `IN_15` | FourBitSwitch | 15 | Upper nibble max |
| `IN_MAX` | device TBD (e.g. thruster at max) | 65535 | Add only when needed |
| `VD_0`–`VD_15` | ValueDisplay ×16 | output only | Read device outputs |

Extended probes (large cable inputs, power inputs, vectors) are added
one-at-a-time when first required by a specific device RE session. Each
is recorded in the agent under **Extended Probe Table** before proceeding.

---

## Setup Session

Run the DeviceRE agent in **Mode C — Setup** to be guided through this.
The session is interactive: the agent asks you to place one device at a
time, you save, the agent reads the save and records the wire UUID.

### Phase 1 — Clear & baseline

1. Remove **all** devices from the Engine Room (leave room-frame type=1 and
   any fixed power network intact if it cannot be removed).
2. Save the game.
3. Tell the agent **"room cleared"**. Agent reads the save and records the
   new baseline UUID set.

### Phase 2 — Add IN probes (IN_0 through IN_15)

For N = 0 to 15, the agent says:
> "Place a FourBitSwitch in the Engine Room, set all toggles to give value N, and save."

After each save the agent:
- Detects the new device UUID (diff against baseline)
- Reads its `indexedChildren` to find the output wire UUID
- Records `IN_N = '<wire-uuid>'` in its probe table

### Phase 3 — Add VD probes (VD_0 through VD_15)

Same process: one ValueDisplay at a time. Agent records `VD_N = '<wire-uuid>'`.

### Phase 4 — IN_MAX (optional, add when needed)

If a device under test requires a 65535 input: agent asks you to place a
suitable constant-max source (e.g. a thruster at full, or any device whose
output is always 65535). Agent records `IN_MAX = '<wire-uuid>'`.

---

## How the Table Is Used During RE

During a device RE session:

1. You wire the device's input ports to chosen `IN_x` probes, output ports
   to `VD_x` probes, and save.
2. Agent auto-detects the new device UUID (diff against baseline).
3. Agent runs the port dump script and inspects each port's wire UUID.
4. For each wire UUID — it **looks it up in the probe table**. No asking
   "what value did you set?" because the value is a recorded constant.
5. Semantic assignment is immediate:
   - Wire matches `IN_3` → input receives value 3
   - Wire matches `VD_1` → output connected to VD_1
6. Agent states the confirmed port map and proceeds to implementation.

### Adding inputs/outputs beyond the standard table

If a new device needs e.g. a large-cable input or a power port that has no
existing probe:
1. Agent asks you to place the required probe device, guides wiring, you save.
2. Agent records the new constant in **Extended Probe Table** in the agent file.
3. Only then does the RE of the target device proceed.

---

## Updating the Probe Table

Wire UUIDs are stored directly in the DeviceRE agent file under
**Probe Wire Table**. To add or correct an entry, run Mode C — Setup
(or run the per-device extended-probe flow) and the agent updates the
table in-place.

**Never edit wire UUIDs manually** — always re-read from save to confirm.
