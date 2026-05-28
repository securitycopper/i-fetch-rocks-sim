# devices/data_processing

Computational devices that transform signal values. These devices read one or
more input ports, compute a result, and write it to one or more output ports on
every tick that their inputs change.

## Subpackages

| Package | Device class(es) | Description |
|---|---|---|
| `binary/` | `BinaryAnd`, `BinaryOr`, `BinaryXor`, `BinaryShift`, `BinaryMux`, `Equality` | Bitwise operations on 16-bit integer signals |
| `generators/` | `QuantumChannelA`–`D` | Constant-value signal generators (quantum oscillator channels) |
| `logic/` | `LogicalAnd`, `LogicalOr`, `LogicalNot`, `LogicalXorGate`, `LogicalXnorGate`, `LogicalNandGate`, `LogicalNor`, `LogicalMux` | Boolean logic gates operating on 0/1 signals |
| `math/arithmetic/` | `Add`, `Minus`, `Multiply`, `Divide`, `Lerp`, `PercentMultiply` | Arithmetic operations on 16-bit values (wrapping at 65535) |
| `math/scoped/` | `SignalInequalities` | Comparison operators (greater-than, less-than, etc.) |
| `math/vector_arithmetic/` | *(vector math devices)* | Arithmetic on large-bus (16-element) vector signals |
| `memory/` | `Register`, `SmallLoopBreak`, `LargeLoopBreak`, `MemoryBaySignal`, `MemoryBayVector` | Latching registers, loop-break latches, and 65k-word memory bays |
| `memory/drives/` | `DriveCartridge` | Read-only drive cartridge attached to a memory bay |
| `sensors/` | `GasSensor` | Environmental sensor returning a room-level reading |
