# SDL Patch Guide

## Purpose
Patch is the controlled, structured, local editing mechanism for SDL.
It reduces the risk of broad free-form rewrites while preserving SDL as authoritative text.

## Architectural Position
Patch workflow does not conflict with SDL authority.
Recommended flow:

`SDL file -> parse -> runtime structured form -> apply patch -> validate -> write back SDL`

## Patch Design Principles
- Local intent only: each patch should target one bounded semantic change.
- Stable targeting: use RefPath and instance/module identifiers.
- Deterministic output: writing back SDL should preserve semantic equivalence and stable ordering.
- Validation-gated: every applied patch must run semantic checks.

## Patch Operation Examples
### addInstance
```json
{
  "op": "addInstance",
  "module": "STM32_Min_System",
  "instance": {
    "id": "c_vdd_c",
    "type": "C",
    "args": {"value": "100nF"},
    "tags": {"role": "decoupling"}
  }
}
```

### removeInstance
```json
{
  "op": "removeInstance",
  "target": "STM32_Min_System.r_boot0"
}
```

### addNet
```json
{
  "op": "addNet",
  "module": "USB_Input_Block",
  "name": "shield_gnd",
  "endpoints": ["j_usb.shield", "gnd"]
}
```

### connectEndpoints
```json
{
  "op": "connectEndpoints",
  "module": "Sensor_I2C_Block",
  "from": "i2c.scl",
  "to": ["u_sensor.scl", "r_scl.2"]
}
```

### disconnectEndpoints
```json
{
  "op": "disconnectEndpoints",
  "module": "Sensor_I2C_Block",
  "from": "i2c.sda",
  "to": ["r_sda.2"]
}
```

### exposeRef
```json
{
  "op": "exposeRef",
  "module": "Debug_Block",
  "source": "j_swd.swd",
  "as": "swd"
}
```

### addConstraint
```json
{
  "op": "addConstraint",
  "module": "LDO_Block",
  "statement": "constrain net vout_main ripple < 40mV"
}
```

### addRequirement
```json
{
  "op": "addRequirement",
  "module": "USB_Input_Block",
  "statement": "require protection for j_usb"
}
```

### addPlacementHint
```json
{
  "op": "addPlacementHint",
  "module": "USB_Input_Block",
  "statement": "place d_usb near j_usb"
}
```

### createPowerDomain
```json
{
  "op": "createPowerDomain",
  "module": "Top_Board_With_Submodules",
  "domain": {
    "name": "board_power",
    "class": "Power",
    "source": "usb0.vbus_out",
    "return": "pwr.gnd",
    "provider": ["usb0", "pwr0"],
    "consumers": ["mcu0", "dbg0", "sns0"]
  }
}
```

### insertIntoTopology
```json
{
  "op": "insertIntoTopology",
  "module": "USB_Input_Block",
  "topology": "usb_dp",
  "after": "j_usb.dp",
  "node": "cm_choke.dp"
}
```

## Conflict Handling
- If two patches target the same RefPath with incompatible operations, reject with conflict diagnostics.
- Resolve by re-parsing latest SDL, rebasing patch intent, and re-validating.
