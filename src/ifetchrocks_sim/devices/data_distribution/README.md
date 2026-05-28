# devices/data_distribution

Passive data-routing devices. These devices move or reshape signals without
applying logic — they connect sources to sinks, split one wire into many,
merge many wires into one, or relay signals wirelessly between rooms.

## Subpackages

| Package | Device class(es) | Description |
|---|---|---|
| `data_conduits/` | `WideConduit`, `TallConduit`, `LargeConduit`, `LargeConduitStub` | Straight-through signal conduits of various widths |
| `data_mergers/` | `BinaryMerger`, `ChannelMerger`, `PacketVectorMerger` | Combine multiple input signals into one output |
| `data_splitters/` | `BinarySplitter`, `ChannelSplitter`, `FlightSplitter`, `MultiplexSplitter`, `PacketVectorSplitter`, `SingleChannelSplitter` | Fan one input signal out to multiple outputs |
| `wireless/` | `WirelessTransmitter`, `WirelessReceiver` | Transmit and receive signals across room boundaries without physical cables |
