# Ship Topology — Career Save `d88a1650`

Derived from reverse-engineering the career save JSON (`game_app_data/Saves/d88a1650-10b4-4d00-8c31-f69b4b41dee2.json`).  
Investigation script (temporary): `rooms_info.py` in the project root.

---

## Physical Ship Layout

The ship has 6 main rooms plus a wireless Server Room (physically not on the ship).  
The z-axis is the front-to-back axis (more negative = further forward).

```
                  ┌─────────────────────┐
                  │   Helm (front)      │  z ≈ -10
                  │   3de44b84  163p    │
                  └──────────┬──────────┘
                             │  large data cable(s)
                  ┌──────────▼──────────┐
                  │   Life Support      │  z ≈ -8
                  │   71bf00a3  200p    │  ← CPU project lives here
                  └──────────┬──────────┘
              ┌──────────────┼──────────────┐
     ┌────────▼────────┐  ┌──▼──────────┐  ┌──────────▼──────┐
     │  Left Thruster  │  │  Central    │  │ Right Thruster  │  z ≈ -5
     │  bad538b2  57p  │  │  3cd1e5ba   │  │  f0343e44  61p  │
     └─────────────────┘  │  46p (16x   │  └─────────────────┘
                           │  passthru) │
                           └──────┬─────┘
                                  │
                  ┌───────────────▼───────────────┐
                  │  Dampeners & Shielding         │  z ≈ -2.5
                  │  d002848a  62p                 │
                  └───────────────┬───────────────┘
                                  │
                         [Engine area rooms]  z ≈ 0
                         73329139 18p, c33bced5 29p
                         (likely Engine + small utility rooms)

  [Wireless/off-ship]  Server Room (no physical position on ship)
```

---

## Room Registry

| Name | UUID (short) | Full UUID | z pos | x pos | Port count | Notes |
|---|---|---|---|---|---|---|
| Helm | `3de44b84` | `3de44b84-84b2-41cd-85fa-33909effbd36` | -10.2 | 0 | 163 | Frontmost room |
| Life Support | `71bf00a3` | `71bf00a3-e017-4c7e-bfa7-32acbddf7047` | -7.6 | 0 | 200 | CPU project, Room.py models this |
| Left Thruster | `bad538b2` | `bad538b2-80e4-4abf-8575-d880206097e8` | -5.0 | -2.5 | 57 | |
| Central Room | `3cd1e5ba` | `3cd1e5ba-7dc8-4aa3-8d39-b457a49dd03d` | -5.0 | 0 | 46 | 16 passthrough cables |
| Right Thruster | `f0343e44` | `f0343e44-1dee-4c41-8b84-7a579f01f772` | -5.0 | +2.7 | 61 | |
| Dampeners | `d002848a` | `d002848a-f75e-47da-a221-22d1d2107dbf` | -2.5 | 0 | 62 | |
| Engine area A | `73329139` | `73329139-d02e-46a2-b1cb-1aa508d25b8c` | 0 | -1.7 | 18 | |
| Engine area B | `c33bced5` | `c33bced5-78e4-4901-9666-c55b353b8831` | 0 | 0 | 29 | |
| Small rooms | `1ec5c991`, `5ec0da90`, `3a10ba9e` | — | 0 | 0–1 | 1–4 | Utility/access |
| *(Unused/wireless)* | `95dae968`, multiple | — | 100,100,100 or (-5,2,0) | — | 0 | No ports; likely Server Room template or empty |

---

## Cable Architecture (Key Finding)

### Same-room passthrough pattern

When a cable **passes through** a room without terminating there (entering one side,
exiting the other), the game save records both wall-portal entries as the **same wire UUID**
in the room's `indexedChildren`.

**Example — Central Room (`3cd1e5ba`) has 16 passthrough cables:**
```
port 1643674487  →  wire 5d2e0e58   ──┐
port -467717284  →  wire 5d2e0e58   ──┘  same wire = passthrough
```
Devices in Life Support or Dampeners that connect to wire `5d2e0e58` are effectively
on the same network, with Central Room completely transparent.

**Simulator consequence:** No special `Room.update_and_notify()` logic is needed for
passthrough cables — the save data already merges both ends to one wire UUID.

### Terminal cable pattern

When a cable **terminates** in a room (both ends connect to devices inside that room),
each cable port has a **distinct** wire UUID. Life Support has 200 ports and only 
**one** shared wire pair — meaning almost all cables in LS are terminal.

**Example — Life Support large data cable:**
```
port -325482860  →  wire 60b2e319  (Large Cable IN, labelled "Left Front-to-Back")
port  1207760765 →  wire e935db8d  (Large Cable OUT, labelled "Left Front-to-Back")
```
These are two different wires → they connect to devices inside Life Support, not to
each other. No Room bridging required; devices inside LS directly use these wire UUIDs.

### Cross-room wire sharing: none found

Zero wire UUIDs are shared between **different** rooms' `indexedChildren` in this save.  
Every shared wire entry is intra-room (both ports on the same room).

**Interpretation:** Cross-room connections are handled by the same-room passthrough
pattern described above, not by sharing wire UUIDs across room boundaries.

---

## Life Support — Known Port IDs

These port IDs are hardcoded in `code/ifetchrocks/sim/devices/Room.py`.
All confirmed present in room `71bf00a3` (Life Support).

| Port ID | Label in Room.py | Wire UUID |
|---|---|---|
| `-325482860` | Large Cable IN Left (Front-to-Back) | `60b2e319-ba96-44f9-9257-11c317032b7e` |
| `1207760765` | Large Cable Out Left (Front-to-Back) | `e935db8d-2804-4321-ab90-de6a014b7c02` |
| `65878718` | Life Support Power | `f4bdbd9f-3f68-4464-bd91-60540c260fc2` |
| `-633974235` | Power Large Cable In Left | `73b3bbad-f159-4324-89ff-a1c96f5fdd9f` |
| `1186959326` | Light | `4332ed05-b323-4138-8f7f-4d03bbe8ea71` |

Port `31010700` ("Life Support Data Out") is referenced in `Room.py`'s `network_out_descriptions`
but was **not found** in the Life Support room's `indexedChildren`. It may be an internal
device (e.g. a `NetworkNode` inside LS whose UUID is `31010700`-derived) rather than a room port.

---

## Room.py — Current State and Design Issue

`code/ifetchrocks/sim/devices/Room.py` (type 1) was written to model Life Support as a
"ChannelMerger-like" device that merges large and small cable inputs and outputs to a
large cable output. This design is incorrect:

1. **`large_output_networks = []` and `large_input_networks = []` are always empty** —
   `update_and_notify()` and the listener registration are both dead code.

2. **All rooms share type ID = 1** — Room.py is instantiated for all 22 rooms, but most
   rooms have no signal-processing role. The ChannelMerger model only makes sense if a room
   were explicitly aggregating inputs, which none of the room types appear to do.

3. **Passthrough cables don't need bridging** — as noted above, same-room shared wire UUIDs
   already handle passthroughs. Room.py doesn't need to bridge IN→OUT for those cables.

4. **Terminal cables don't need bridging either** — their wire UUIDs connect directly to
   the devices inside the room.

**Recommendation:** Room.py should be a no-op placeholder that just exposes its port UUIDs
as attributes (already done) without attempting signal routing. The `update_and_notify`
method and listener registration can remain as dead code or be removed.

The only case where Room.py would need logic is if a cable comes from the outside AND needs
routing to a small-cable sub-network within the same room (e.g. speaking a received large
packet down to a small-cable device). That use case has not been observed in the career save.

---

## External Devices Reachable from Life Support

Based on the cable topology and the CPU program's `SEND_EXTERNAL_DEVICE` / `READ_EXTERNAL_DEVICE`
calls, Life Support's CPU connects to the following external devices:

| Device | Location | Path |
|---|---|---|
| Spectroscope | Helm | LS cable OUT → (passthrough rooms?) → Helm |
| Thrusters | Left/Right Thruster rooms | LS → Central (passthrough) → Thruster rooms |
| Speakers | Unknown — likely in Central or Helm | TBD |
| Navigation sensors | Helm/Central | TBD |
| Front Display | Helm | TBD |

The exact wire UUIDs for these paths have not yet been traced. Use the career save debugger
to observe which wires carry values during a CPU execution run.

---

## Simulator Support Status

| Feature | Status | Notes |
|---|---|---|
| Room as no-op | ✅ (accidentally) | `large_input/output_networks = []` means no action |
| Cable passthrough (Central Room) | ✅ | Shared wire UUID already works |
| Terminal cable access (Life Support) | ✅ | Devices connect to wire UUIDs directly |
| Speaker device | ❌ stub | No `output_networks`, no `update_and_notify` |  
| `START_STREAM` / `PROCESS_STREAM` opcodes | ❌ unhandled | No simulator dispatcher |
| External device routing (`SEND_EXTERNAL_DEVICE`) | ❌ not wired | No handler maps device ID → wire UUID |
| Cross-room data tracing | ⚠️ investigation needed | Must trace wire UUIDs room-by-room |
