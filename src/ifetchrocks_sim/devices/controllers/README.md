# devices/controllers

Player-operated input devices. Each controller device exposes one or more output
ports whose values are driven by the in-game save state (the current switch
position, dial value, etc.).

## Subpackages

| Package | Device class(es) | Description |
|---|---|---|
| `buttons/` | `ButtonSingle`, `FourButtonBank` | Momentary push buttons |
| `dials/` | `ControllerDial` | Rotary dial with a numeric output |
| `joysticks/` | `TwoAxisJoystick`, `HorizontalAxisJoystick`, `VerticalAxisJoystick`, `Throttle` | Analogue joystick axes |
| `sliders/` | `SmallSlider`, `WideSlider` | Linear slider inputs |
| `special/` | `CargoGunController` | Specialised cargo-gun firing controller |
| `switches/` | `SwitchSingle`, `OneBitSwitch`, `FourBitSwitch`, `FourToggleSwitch`, `EightBitSwitch` | Binary and multi-bit toggle switches |
