# Room Port Map — Inter-Room Wire Topology (roomRE)

Census date: 2026-03-29.  
Saves analysed (identical results across both):
- functional: `game_app_data/Saves/584e4a42-287c-4c1e-a48f-ab62b1f3ded3.json`
- career: `game_app_data/Saves/d88a1650-10b4-4d00-8c31-f69b4b41dee2.json`

## Key findings

**Inter-room wire connections are NOT stored as shared UUIDs in the save JSON.**
Every large-cable wall socket has a unique UUID within its own room. The
physical in-game cable connecting two rooms is only represented by the 3D
geometry of the cable mesh, which is not serialised. As a result, every
cross-room large cable appears as `DANGLING` when analysed from the save JSON
alone.

To establish the connection map, two approaches are available:
1. **In-game RE** — re-lay a cable in-game, save, and check whether both room
   endpoints now share a UUID. (Current evidence suggests they will not, but
   this should be tested manually.)
2. **Circuit-direction RE** — determine IN vs OUT for each wall socket by
   inspecting which simulator device produces or consumes the large network,
   then match OUTs to INs by room topology knowledge and physical
   corridor layout.

All rooms listed below are **type-1** (room frame). Only rooms with at least one
large-data cable (type-4) wall socket are included.

---

## How to read the port direction conventions in Room.py

Room.py uses misleading naming inherited from an earlier draft:

| Room.py name | Save JSON port key | Actual flow |
|---|---|---|
| `large_network_out_0_left_front_to_back` | `-325482860` | Data flows **into** the room (the room is a consumer, not a producer) |
| `large_network_in_0_left_front_to_back` | `1207760765` | Data flows **out of** the room (the room is a producer, not a consumer) |

The naming is inverted relative to the data flow. Use the simulator circuit
analysis (produced_by / consumed_by device) as ground truth.

---

## Room inventory

### Room `71bf00a3` — Life Support (CPU + decoder)

200 children. Contains the entire CPU, ChannelMerger `56816edd`, ChannelSplitter `457a8e44`.

| Port key | Cable UUID | Direction | Inner device | Semantic | Paired room | Status |
|---|---|---|---|---|---|---|
| `-325482860` | `60b2e319` | **IN** | ChannelSplitter `457a8e44` (instruction bus) | Instruction word bus arriving from Helm (large 16-ch) | `3de44b84` Helm ? | TODO |
| `789320731` | `ffb0b67f` | **IN** | ChannelMerger `56816edd` (large input) | External sensor data arriving from hub/central | `3cd1e5ba` Hub ? | TODO |
| `1207760765` | `e935db8d` | **OUT** | ChannelSplitter `457a8e44` (output) | Decoded command bus leaving toward Helm | `3de44b84` Helm ? | TODO |
| `-1631889157` | `0e935799` | **OUT** | ChannelMerger `56816edd` (output) | Merged sensor/result bus leaving toward hub/central | `3cd1e5ba` Hub ? | TODO |

Also present in Room.py (already labeled):
- Port `65878718` — large power IN (Life Support power)
- Port `-633974235` — large power OUT (bottom-left power distribution)
- Port `31010700` — small data OUT (Life Support data out)
- Port `1186959326` — small power IN (room light)

---

### Room `3de44b84` — Helm

163 children. Contains ChannelSplitters (`19392cc9` etc.), navigation sensors, thruster controls.  
Note: `52b8da0d` appears at **two** port keys in the same room — it is a same-room pass-through (cable enters one Helm wall, exits another Helm wall without leaving the room instance).

| Port key | Cable UUID | Direction | Inner device | Semantic | Paired room | Status |
|---|---|---|---|---|---|---|
| `1929969497` | `52b8da0d` | **IN** | Room boundary only | One end of Helm internal pass-through | same room `-1570675167` | CONFIRMED pairs internally |
| `-1570675167` | `52b8da0d` | **IN** | Room boundary only | Other end of Helm internal pass-through | same room `1929969497` | CONFIRMED pairs internally |
| `-1441170788` | `11d4df6a` | **IN** | ChannelSplitter `19392cc9` | Instruction/command bus arriving from Life Support ← `e935db8d` ? | `71bf00a3` LS ? | TODO |

---

### Room `bad538b2` — Thruster Room A

57 children. One large cable IN, no OUT. Likely a thruster room consuming command signals.  
Device composition: ChannelMerger (`67`), BinaryMerger (`115`), ChannelSplitter-like, many NetworkNodes.

| Port key | Cable UUID | Direction | Inner device | Semantic | Paired room | Status |
|---|---|---|---|---|---|---|
| `-502849257` | `8e66002c` | **IN** | Room boundary only — UnknownDevice | Command bus input (thruster commands?) | Unknown | TODO |

---

### Room `f0343e44` — Thruster Room B

61 children. One large cable OUT (from ChannelMerger `6adf0794`) + one large cable IN.  
Device composition: same signature as `bad538b2` plus type-101 device. Likely a thruster room with feedback.

| Port key | Cable UUID | Direction | Inner device | Semantic | Paired room | Status |
|---|---|---|---|---|---|---|
| `-1886394471` | `a414d894` | **OUT** | ChannelMerger `6adf0794` (produces it) | Thruster feedback / status output | `3cd1e5ba` Hub ? | TODO |
| `-451546198` | `72e0af92` | **IN** | Room boundary only — UnknownDevice | Thruster command input | `3cd1e5ba` Hub ? | TODO |

---

### Room `d002848a` — Sensor / I/O Room

62 children. One large cable IN. Contains 18 Registers, WirelessTransmitter (type 212), Registers, BinaryMux, ChannelSplitter.  
Likely a spectroscope/sensor room receiving commands and reporting values wirelessly.

| Port key | Cable UUID | Direction | Inner device | Semantic | Paired room | Status |
|---|---|---|---|---|---|---|
| `-71024863` | `254e6cb2` | **IN** | Room boundary only — UnknownDevice | Command/address bus input | Unknown | TODO |

---

### Room `3cd1e5ba` — Junction / Hub Room

46 children. **Type-2 and type-3 power nodes only, plus type-4 large cable sockets.**  
No computational devices — acts as a pure cable pass-through hub. 8 large cable UUIDs, each appearing at exactly 2 wall sockets (enter one wall, exit another).

| Cable UUID | Port key A | Port key B | Semantic | Connects (from) | Connects (to) | Status |
|---|---|---|---|---|---|---|
| `5611773b` | `-1812790686` | `-622941254` | Unknown pass-through | ? | ? | TODO |
| `4df3e57a` | `468632222` | `1722912596` | Unknown pass-through | ? | ? | TODO |
| `9ca964c7` | `1181792048` | `-503289276` | Unknown pass-through | ? | ? | TODO |
| `bf9d5e28` | `-2054379047` | `-167838602` | Unknown pass-through | ? | ? | TODO |
| `a1dc17a3` | `-1752912888` | `516810063` | Unknown pass-through | ? | ? | TODO |
| `387eb408` | `-201532224` | `924592864` | Unknown pass-through | ? | ? | TODO |
| `79a9a846` | `-469054008` | `1469552175` | Unknown pass-through | ? | ? | TODO |
| `e87d60e5` | `1123937667` | `-616421510` | Unknown pass-through | ? | ? | TODO |

---

## Cross-room pairing hypothesis (circuit-direction based)

Based on direction analysis, the following pairings are structurally consistent.
All marked HYPOTHESIS until confirmed by in-game RE.

| OUT room | OUT cable | → | IN room | IN cable | Confidence | Status |
|---|---|---|---|---|---|---|
| LS `71bf00a3` | `e935db8d` (ChannelSplitter out) | → | Helm `3de44b84` | `11d4df6a` (ChannelSplitter in) | HIGH — both are decoded command buses | HYPOTHESIS |
| Helm `3de44b84` | (unknown Helm output) | → | LS `71bf00a3` | `60b2e319` (instruction bus in) | HIGH — instruction words flow Helm→LS | HYPOTHESIS |
| LS `71bf00a3` | `0e935799` (ChannelMerger out) | → | Hub `3cd1e5ba` | one of 8 hub cables | MEDIUM | HYPOTHESIS |
| Hub `3cd1e5ba` | (one of 8) | → | LS `71bf00a3` | `ffb0b67f` (ChannelMerger large in) | MEDIUM | HYPOTHESIS |
| Hub `3cd1e5ba` | (one of 8) | → | Thruster A `bad538b2` | `8e66002c` (in) | LOW | HYPOTHESIS |
| Thruster B `f0343e44` | `a414d894` (ChannelMerger out) | → | Hub `3cd1e5ba` | (one of 8) | LOW | HYPOTHESIS |
| Hub `3cd1e5ba` | (one of 8) | → | Thruster B `f0343e44` | `72e0af92` (in) | LOW | HYPOTHESIS |
| Hub `3cd1e5ba` | (one of 8) | → | Sensor `d002848a` | `254e6cb2` (in) | LOW | HYPOTHESIS |

### Note on Helm internal pass-through (`52b8da0d`)

`52b8da0d` appears at two port keys within the Helm room only (`1929969497` and
`-1570675167`). This is a Helm-internal cable bridge — likely connecting two
Helm wall sockets that route through the adjacent corridor without leaving the
Helm room instance. Both sides are consumed as room-boundary-only by the Room
class, not by any active device, suggesting this cable is power or unused data.

---

## RE workflow for confirming pairings

For each HYPOTHESIS row, the following steps would confirm or deny it:

1. In-game: note the UUID shown on both ends of a cable you can see connecting
   two rooms (if the game UI exposes it).
2. Re-lay the cable, export a new save, run `_probe_room_topology.py` and check
   whether both rooms now share that cable UUID.
3. If they do share it — the pairing is confirmed and the simulator can wire it
   automatically.
4. If they still don't share it — cross-room connections are stored purely in
   3D geometry and must be hardcoded in a `CROSS_ROOM_BRIDGES` table in
   `simulator.py`.

---

## Simulator fix plan (once pairings are confirmed)

Add a `CROSS_ROOM_BRIDGES` mapping to `simulator.py`:

```python
# Maps (source_large_net_uuid_prefix, sink_large_net_uuid_prefix)
# Applied after load_from_file() to bridge dangling room wall cables.
CROSS_ROOM_BRIDGES = [
    # ('0e935799', '60b2e319'),  # HYPOTHESIS: LS ChannelMerger OUT → LS ChannelSplitter IN
    # Confirmed pairs will go here once RE is done
]
```

And in `load_from_file` / `for_career_save`, call:

```python
for src_prefix, dst_prefix in CROSS_ROOM_BRIDGES:
    src = self._find_large_net(src_prefix)
    dst = self._find_large_net(dst_prefix)
    if src and dst:
        src.register_listener(lambda uuid, val, d=dst: d.update_source('room_bridge', val))
        dst.update_source('room_bridge', src.value)
```
