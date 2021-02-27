// @flow

const airspeedSchema = {
  type: ['null', 'object'],
  title: 'Airspeed',
  description: 'Plane\'s Airspeed',
  required: ['airvx', 'airvy', 'airvz', 'speed', 'climb'],
  properties: {
    airvx: {type: 'number'},
    airvy: {type: 'number'},
    airvz: {type: 'number'},
    speed: {type: 'number'},
    climb: {type: 'number'},
    time: {type: 'number'},
    throttle: {type: 'number'}
  }
};

const batterySchema = {
  type: ['null', 'object'],
  title: 'Battery',
  description: 'Motor Battery Info',
  required: ['batteryvoltage', 'batterypct'],
  properties: {
    batteryvoltage: {type: 'number'},
    batterypct: {type: 'number'},
    time: {type: 'number'}
  }
};

const attitudeSchema = {
  type: ['null', 'object'],
  title: 'Attitude',
  description: 'Plane\'s Orientation',
  required: ['roll', 'pitch', 'yaw', 'rollspeed', 'pitchspeed', 'yawspeed'],
  properties: {
    roll: {type: 'number'},
    pitch: {type: 'number'},
    yaw: {type: 'number'},
    rollspeed: {type: 'number'},
    pitchspeed: {type: 'number'},
    yawspeed: {type: 'number'},
    time: {type: 'number'}
  }
};

const linkObjectSchema = {
  type: 'object',
  description: 'Individual Link Connection',
  title: 'Link Object',
  required: ['packet_loss', 'alive', 'device_name', 'num', 'device', 'num_lost',
    'link_delay'],
  properties: {
    packet_loss: {type: 'number'},
    alive: {type: 'boolean'},
    device_name: {type: 'string'},
    num: {type: 'number'},
    device: {type: 'string'},
    num_lost: {type: 'integer'},
    link_delay: {type: 'number'}
  }
};

const linkSchema = {
  type: ['null', 'object'],
  description: 'Link to the plane and GPS',
  title: 'Connection Link',
  required: ['plane_link', 'links', 'gps_link'],
  properties: {
    plane_link: {type: 'boolean'},
    gps_link: {type: 'boolean'},
    links: {
      type: 'array',
      items: linkObjectSchema
    }
  }
};

const windSchema = {
  type: ['null', 'object'],
  description: 'Plane\'s wind readings',
  title: 'Wind',
  required: ['windvx', 'windvy', 'windvz'],
  properties: {
    windvx: {type: 'number'},
    windvy: {type: 'number'},
    windvz: {type: 'number'},
    time: {type: 'number'}
  }
};

const gpsSchema = {
  type: ['null', 'object'],
  description: 'GPS Information',
  title: 'GPS',
  required: ['rel_alt', 'asl_alt', 'lat', 'lon', 'heading', 'groundvx',
    'groundvy', 'groundvz'],
  properties: {
    'rel_alt': {type: 'number'},
    'asl_alt': {type: 'number'},
    'lat': {type: 'number'},
    'lon': {type: 'number'},
    'heading': {type: 'number'},
    'groundvx': {type: 'number'},
    'groundvy': {type: 'number'},
    'groundvz': {type: 'number'},
    'time': {type: 'number'}
  }
};

export const statusSchema = {
  type: 'object',
  title: 'Status Schema',
  '$schema': 'http://json-schema.org/draft-06/schema#',
  description: 'Schema describing full status object',
  required: ['airspeed', 'battery', 'attitude', 'link', 'armed', 'throttle',
    'current_wp', 'mode', 'wind', 'gps', 'mav_info', 'mav_warning', 'mav_error',
    'gps_status', 'signal', 'safe'],
  properties: {
    airspeed: airspeedSchema,
    battery: batterySchema,
    attitude: attitudeSchema,
    link: linkSchema,
    armed: {type: ['null', 'boolean']},
    throttle: {type: ['null', 'number']},
    current_wp: {type: ['null', 'number']},
    mode: {type: ['null', 'string']},
    wind: windSchema,
    gps: gpsSchema,
    mav_info: {type: ['null', 'string']},
    mav_warning: {type: ['null', 'string']},
    mav_error: {type: ['null', 'string']},
    gps_status: {
      type: ['null', 'object', 'integer'],
      required: ['satellite_number'],
      properties: {
        satellite_number: {type: 'integer'}
      }
    },
    signal: {
      type: ['null', 'object'],
      required: ['signal_strength'],
      properties: {
        signal_strength: {type: 'integer'}
      }
    },
    safe: {type: ['null', 'boolean']}
  }
};

const waypointObjectSchema = {
  type: 'object',
  title: 'Waypoint object',
  description: 'Individual waypoint'
};

export const waypointsSchema = {
  type: 'array',
  items: waypointObjectSchema
};

export const gimbalSchema = {
  type: 'string'
};

export const fenceSchema = {
  type: 'array',
  items: {
    type: 'object',
    required: ['lat', 'lon'],
    properties: {
      lat: {type: 'number'},
      lon: {type: 'number'}
    }
  }
};

const obstacleSchema = {
  type: 'object',
  required: ['latitude', 'longitude', 'radius', 'height'],
  properties: {
    latitude: {type: 'number'},
    longitude: {type: 'number'},
    radius: {type: 'number'},
    height: {type: 'number'}
  }
};

export const interopSchema = {
  type: 'object',
  title: 'Interop Schema',
  description: 'Interface with interop server',
  required: ['obstacles', 'server_working', 'active', 'mission_waypoints',
    'mission_wp_dists', 'active_mission'],
  properties: {
    obstacles: {
      stationary_obstacles: {
        type: 'array',
        items: obstacleSchema
      }
    },
    server_working: {type: 'boolean'},
    hz: {type: 'number'},
    active: {type: 'boolean'},
    mission_waypoints: {type: 'array'},
    mission_wp_dists: {
      type: 'array',
      items: {type: 'number'}
    }
  }
};

const pointObject = {
  type: 'object',
  title: 'Point Object',
  required: ['lat', 'lon'],
  properties: {
    lat: { type: 'number' },
    lon: { type: 'number' }
  }
};

const distributedPointObject = {
  type: 'object',
  title: 'Point Object',
  required: ['latitude', 'longitude'],
  properties: {
    latitude: { type: 'number' },
    longitude: { type: 'number' }
  }
};

const splineObject = {
  type: 'array',
  items: pointObject,
  maxItems: 4,
  minItems: 4
};

export const splineSchema = {
  type: 'object',
  title: 'Spline Schema',
  description: 'Retrieve splines for plotting',
  required: ['splines'],
  properties: {
    splines: {
      type: 'array',
      items: splineObject
    }
  }
};

export const regionSchema = {
  type: 'object',
  title: 'Region API',
  required: ['mdlc', 'adlc'],
  properties: {
    mdlc: {
      type: 'object',
      required: ['high', 'medium', 'low'],
      properties: {
        high: {
          type: 'array',
          items: distributedPointObject
        },
        medium: {
          type: 'array',
          items: distributedPointObject
        },
        low: {
          type: 'array',
          items: distributedPointObject
        }
      }
    },
    adlc: {
      type: 'array',
      items: distributedPointObject,
      maxItems: 5
    }
  }
};

export const airdropSchema = {
  type: 'object',
  title: 'Airdrop Schema',
  required: ['status', 'gpsTargetLocation', 'isArmed'],
  properties: {
    status: {
      type: 'string',
      enum: ['sent', 'failed', 'queued']
    },
    gpsTargetLocation: distributedPointObject,
    isArmed: { type: 'boolean' }
  }
};
