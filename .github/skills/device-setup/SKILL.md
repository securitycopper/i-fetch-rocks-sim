---
name: device-setup
description: "Reverse-engineer a new device in ifetchrocks-sim. Use when: user has placed a device in the Engine Room RE save, wired it to probes, and is describing what device it is and how they set it up. Keywords: device RE, reverse engineer, port ID, probe wire, Engine Room, new device, device type, place device, wire probes, FourBitSwitch, ValueDisplay, port key."
argument-hint: "Describe the device you placed, e.g. 'type 151, wired IN_0 to first input, VD_0 to output' or 'LogicalMux, 3 inputs 1 output'"
---

# Device Setup RE — Interactive Skill

Guided reverse-engineering of a newly-placed device in the Engine Room RE save.
The user places the device in-game, wires it to probes, saves, and describes
what they did. The agent reads the save, identifies ports, and drives
implementation in ifetchrocks-sim.

## Reference docs (read first)

- **RE tools API:** `src/ifetchrocks_sim/re_tools.py` — `RESave`, port matching, 
  probe table (`PROBE_WIRES`), and helper functions.
  **Always use this API instead of inline scripts.**
- **Validation:** `src/ifetchrocks_sim/validation.py` — `classify_unknown_devices()`,
  unknown device census.

## Save file

- **RE save (always):** `game_app_data/Saves/102d6094-bff6-413a-b859-b4992647c9e5.json`
- Never ask the user for a save path. Always read this save directly.

---

## Workflow

### Step 1 — User describes what they placed

The user tells you, in any format:
- **Device type** (e.g. "type 151", "LogicalMux", a manual page name)
- **How they wired it** (e.g. "IN_0 to first input, IN_1 to second, VD_0 to output")
- **Any switch/dial settings** (e.g. "set dial to 42", "switch ON")

Accept informal descriptions. The user does NOT need to know port keys — that's
what this skill discovers.

### Step 2 — Detect new devices in the save

Use the `re_tools` API:

```python
from ifetchrocks_sim.re_tools import RESave

re = RESave()  # Loads fixed RE save
new_devices = re.find_new_devices()  # Diff against baseline

if not new_devices:
    print("No new devices detected. Ensure the device was saved in-game.")
else:
    for dev in new_devices:
        print(f"Type {dev.type_id}: {dev.uuid[:8]} at {dev.location}")
```

If multiple new devices, ask the user to narrow down which one they placed.
Then get the single device:

```python
device_info = new_devices[0]
print(f"Device type: {device_info.type_id}")
print(f"UUID: {device_info.uuid}")
```

### Step 3 — Match ports to probes

Use `re_tools` to match the wired probes and extract port IDs:

```python
from ifetchrocks_sim.re_tools import RESave

re = RESave()
device_info = re.find_new_devices()[0]

# Get port map with probe annotations
ports = re.port_map(type_id=device_info.type_id)

# Pretty-print it
re.print_port_map(type_id=device_info.type_id)
```

Output shows:
- **Port key** (unique ID for the device's port)
- **Port name** (inferred or named by you)
- **Probe label** (IN_0, VD_3, etc. — tells you what this port does)
- **Network kind** (data, power, large_data, etc.)

### Step 4 — Implement the device

Create a new file in `src/ifetchrocks_sim/devices/<category>/<device_snake_case>.py`.
Use the **port key** and **probe labels** to understand the wiring:

```python
"""Device implementation for type <type_id>."""
from ifetchrocks_sim.devices.template import Device
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connections_uuids_of_type


class MyNewDevice(Device):
    """Type <type_id>: <name>."""

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.name = f"{self.__class__.__name__}"
        
        # Use port keys from step 3 to extract connections
        # Example: port key '1234567890' is the first input
        self.input_uuid_1 = get_connections_uuids_of_type(data, 5)[0]  # network type 5 = data
        
        # Initialize networks
        self.network_in_1 = self.network_manager.get_network(self.input_uuid_1)
        # ... more ports ...
        
        self.value = 0

    def tick(self):
        """Compute output based on input."""
        input_val = self.network_in_1.get_value(self.uuid)
        self.value = input_val  # Or compute derived output
        # Update output network(s)
        # self.network_out.update_source(self.uuid, self.value)

    def change_event(self, component_id: str, large_data_in=None):
        """Handle input changes."""
        self.tick()
```

### Step 5 — Register the device

1. Add import to `src/ifetchrocks_sim/devices/__init__.py`
2. Add type ID to enum in `src/ifetchrocks_sim/simulator.py` (line ~100 `ComponentType`)
3. Add device class to the factory in `simulator.py` (`get_device` function)

### Step 6 — Test

Use CircuitBuilder to write a unit test, or run the simulator:

```python
from ifetchrocks_sim import Simulator

sim = Simulator()
with open('game_app_data/Saves/102d6094-bff6-413a-b859-b4992647c9e5.json') as f:
    sim.load_from_file(f)
    
# Device should be recognized and instantiated now
devices = [d for d in sim.found_devices.values() 
           if type(d).__name__ == 'MyNewDevice']
assert devices, "Device not found after implementation"
```

Run full suite:

```bash
python -m pytest tests/ -v
```
