# devices/power_distribution

Power-supply devices. These devices move electrical power around the ship; they
do not carry data signals. In the simulator they track whether a power path is
live so that power-gated devices can determine their powered state.

## Contents

| Module / Package | Class(es) | Description |
|---|---|---|
| `generator_power_bus.py` | `GeneratorPowerBus` | Central power bus fed by the ship's generator |
| `energy_cells/` | `SmallEnergyCell` | Rechargeable backup power cell |
| `power_splitters/` | `SmallPowerSplitter`, `LargePowerSplitter`, `LongPowerSplitter`, `SmallSwitchedPower`, `LargeSwitched` | Distribute power from one source to multiple outputs; switched variants include a gate input |
| `redundant/` | *(redundancy switch devices)* | Automatic failover between primary and backup power paths |
