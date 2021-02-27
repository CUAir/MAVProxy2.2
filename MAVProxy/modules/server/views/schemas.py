import jsonschema
from pymavlink.mavutil import mavlink
from jsonschema import Draft4Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if "default" in subschema:
                if type(instance) == list:
                    for x in instance:
                        x.setdefault(property, subschema["default"])
                else:
                    instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})


VALID_COMMANDS = [mavlink.MAV_CMD_NAV_LOITER_UNLIM, mavlink.MAV_CMD_NAV_WAYPOINT,
                  mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, mavlink.MAV_CMD_NAV_LAND,
                  mavlink.MAV_CMD_NAV_TAKEOFF]

generic_waypoint = {   # include nav_wp, nav_loiter_unlimited, RTL, land, takeoff
    "type": "object",
    "properties": {
        "alt": {
            "type": "number",
            "minimum": 0,
        },
        "lat": {
            "type": "number",
            "minimum": -180,
            "maximum": 180,
        },
        "lon": {
            "type": "number",
            "minimum": -180,
            "maximum": 180,
        },
        "command": {
            "type": "number",
            "fstype": {"enum": VALID_COMMANDS},
            "default": mavlink.MAV_CMD_NAV_WAYPOINT
        },
        "index": {
            "type": "number",
            "default": -1
        },
        "current": {
            "type": "number",
            "default": 0
        },
        "sda": {
            "type": "boolean",
            "default": False
        }
    },
    "default": {},
    "required": ["alt", "lat", "lon", "command"]
}

do_jump = {
    "type": "object",
    "properties": {
        "alt": {
            "type": "number",
            "minimum": 0,
        },
        "lat": {
            "type": "number",
            "minimum": -180,
            "maximum": 180,
        },
        "lon": {
            "type": "number",
            "minimum": -180,
            "maximum": 180,
        },
        "command": {
            "type": "number",
            "fstype": {"enum": [mavlink.MAV_CMD_DO_JUMP]},
        },
        "index": {
            "type": "number",
            "default": -1
        },
        "current": {
            "type": "number",
            "default": 0
        }
    },
    "default": {},
    "required": ["alt", "lat", "lon", "command"]
}

waypoint = {
    "anyOf": [generic_waypoint, do_jump]
}

waypoint_list = {
    "type": "array",
    "items": waypoint
}

waypoint_or_waypointlist = {
    "anyOf": [waypoint,
              waypoint_list]
}

current = {
    "type": "object",
    "properties": {
        "current": {
            "type": "number",
            "minimum": 0,
        },
    },
    "required": ["current"]
}

timestamp = {
    "timestamp": "number"
}


# Schema for changing a parameter.
# Required downstream check: [parameter] is valid parameter name.
# Required downstream check: [value] is valid for the requested parameter.
parameters = {
    "type": "object",
    "properties": {
        # The parameter name to change.
        # Required field.
        "pname": {
            "type": "string",
        },
        # The value to set the parameter to.
        # Required field.
        "value": {
            "type": "number",
        },
    },
    "required": ["pname", "value"]
}

VALID_MODES = ['RTL', 'TRAINING', 'LAND', 'AUTOTUNE', 'STABILIZE', 'AUTO', 'GUIDED',
               'LOITER', 'MANUAL', 'FBWA', 'FBWB', 'CRUISE', 'INITIALISING', 'CIRCLE', 'ACRO']
mode = {
    "type": "object",
    "properties": {
        "mode": {
            "type": "string",
            "fstype": {"enum": VALID_MODES}
        },
    },
    "required": ["mode"]
}

search_grid = {
    "type": "array"
}

coverage_settings = {
    "type": "object"
}

schemas = {'waypoint_or_waypointlist': waypoint_or_waypointlist,
           'current': current,
           'parameters': parameters,
           'mode': mode}

jsonschema = extend_with_default(Draft4Validator)
