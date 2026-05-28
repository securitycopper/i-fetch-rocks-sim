# devices/data_monitors

Output-only devices that present signal values to the player. These devices
consume input port values and produce no electrical output; their effect is
purely visual or auditory. In the simulator they update internal state so
that diagnostic tools can read their displayed values.

## Subpackages

| Package | Device class(es) | Description |
|---|---|---|
| `displays/` | `ValueDisplay`, `CounterDisplay`, `BooleanLight`, `BinaryLightArray`, `LinearLightArray`, `ElementDisplay`, `Oscilloscope` | Visual readouts — numeric, binary, and waveform displays |
| `speakers/` | `Speaker` | Audio output device; stores the last-received value |
