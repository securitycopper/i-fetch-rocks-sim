# network

Wire-network primitives. The simulator models in-game wiring as a graph of
network objects. Every signal wire is a node in one of these networks; devices
subscribe to node changes and push new values back into the network.

## Modules

| Module | Class | Description |
|---|---|---|
| `data_network.py` | `DataNetwork` | A connected set of 16-bit signal wires. Holds current values and fires change listeners when a value is updated. |
| `large_data_network.py` | `LargeDataNetwork` | Like `DataNetwork` but carries a 16-element integer array (large bus). |
| `data_network_manager.py` | `DataNetworkManager` | Registry of all networks in a loaded save. Devices call `get_or_create` to attach to their wires; the manager routes inter-device signals. |

## Usage

These classes are normally used only inside device implementations and the
`Simulator`. For diagnostic work you can reach them directly:

```python
from ifetchrocks_sim import Simulator, DataNetworkManager

sim = Simulator()
with open("save.json") as f:
    sim.load_from_file(f)

# Find the network a wire prefix belongs to
net = sim.find_network("abcd1234")
print(net.get_value("abcd1234-full-uuid"))
```
