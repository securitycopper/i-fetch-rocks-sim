# devices

All in-game device implementations for the I Fetch Rocks simulator.

Each device class wraps the save-file JSON for one in-game object, wires itself into the `DataNetworkManager`, and reacts to input port changes by computing new output port values. Devices are discovered and instantiated automatically by the `Simulator` when a save file is loaded.

## Subpackages

| Package | Description |
|---|---|
| `controllers/` | Player-operated input devices: buttons, dials, joysticks, sliders, switches |
| `data_distribution/` | Passive routing devices: conduits, mergers, splitters, wireless links |
| `data_monitors/` | Output-only devices that display or play values: displays, speakers |
| `data_processing/` | Computation devices: logic gates, arithmetic, memory, generators, sensors |
| `power_distribution/` | Power supply chain: energy cells, buses, splitters, redundancy switches |
| `utils/` | Internal helpers shared across device categories |

## Shared base types

| Module | Class | Description |
|---|---|---|
| `network_node.py` | `NetworkNode` | Base class for all signal-carrying devices |
| `large_network_node.py` | `LargeNetworkNode` | Base class for devices on the 16-element large bus |
| `network_power_node.py` | `NetworkPowerNode` | Base class for power-carrying devices |
| `Room.py` | `Room` | Room frame node (boundary between rooms) |
| `Template.py` | `Template` | Placeholder / unplaced device template |
| `unknown_device.py` | `UnknownDevice` | Stub for type IDs not yet reverse-engineered |
