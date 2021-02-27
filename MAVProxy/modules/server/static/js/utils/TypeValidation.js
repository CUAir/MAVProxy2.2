// @flow

const NUMBER = 'number';
const STRING = 'string';
const FUNCTION = 'function';
const BOOLEAN = 'boolean';
const UNDEFINED = 'undefined';
const NULL = 'null';
const OBJECT = 'object';

/**
 * @module utils/TypeValidation
 */

function validType(value, type) {
  if (type === BOOLEAN || type === STRING || type === NUMBER ||
      type === FUNCTION || type === UNDEFINED) {
    return typeof value === type;
  } else if (type === NULL) {
    return value === null;
  } else if (Array.isArray(type)) {
    if (type.length >= 1) {
      return value.map(val => validType(val, type[0])).reduce((acc, val) => acc && val, true);
    } else {
      return true;
    }
  } else if (typeof type === OBJECT) {
    return Object.keys(type).reduce((acc, key) => {
      return acc && validType(value[key], type[key]);
    }, true);
  } else {
    return false;
  }
}

/**
 * Makes sure that json is valid and of the correct type
 * @param {string} name - for printout purposes
 * @param {string} stringValue - json to be parsed
 * @param {any} type - the type to be validated against
 * @returns {boolean}
 */
export function assertJson(name: string, stringValue: string, type: any) {
  try {
    const value = JSON.parse(stringValue);
    const valid = validType(value, type);
    if (!valid) {
      console.log(`${name}: Invalid type`); // eslint-disable-line no-console
    }  
    return valid;
  } catch(err) {
    console.log(`${name}: ${err}`); // eslint-disable-line no-console
    return false;
  }
}

/**
 * @typedef {string | Object} ReceiveType */

/** @type {ReceiveType} */
export const airspeedType = {
  airvx: NUMBER,
  airvy: NUMBER,
  airvz: NUMBER,
  speed: NUMBER
};

/** @type {ReceiveType} */
export const attitudeType = {
  pitch: NUMBER,
  roll: NUMBER,
  yaw: NUMBER,
  pitchspeed: NUMBER,
  rollspeed: NUMBER,
  yawspeed: NUMBER
};

/** @type {ReceiveType} */
export const armedType = BOOLEAN;

/** @type {ReceiveType} */
export const batteryType = {
  batteryvoltage: NUMBER,
  batterypct: NUMBER
};

/** @type {ReceiveType} */
export const climbRateType = NUMBER;

/** @type {ReceiveType} */
export const currentWaypointType = NUMBER;

/** @type {ReceiveType} */
export const fenceType = [{
  lat: NUMBER,
  lon: NUMBER
}];

export const flightTimeType = {
  time_start: NUMBER,
  is_flying: BOOLEAN
};

/** @type {ReceiveType} */
export const gpsType = {
  lat: NUMBER,
  lon: NUMBER,
  rel_alt: NUMBER,
  groundvx: NUMBER,
  groundvy: NUMBER,
  groundvz: NUMBER,
  heading: NUMBER
};

export const gpsStatusType = {
  satellite_number: NUMBER
};

/** @type {ReceiveType} */
export const linkType = {
  gps_link: BOOLEAN,
  plane_link: BOOLEAN,
  links: [{
    packet_loss: NUMBER,
    alive: BOOLEAN,
    num: NUMBER,
    device: STRING,
    num_lost: NUMBER,
    link_delay: NUMBER,
    device_name: STRING
  }]
};

/** @type {ReceiveType} */
export const modeType = STRING;

/** @type {ReceiveType} */
export const powerboardType = {
  csbatt: NUMBER,
  nuc: NUMBER,
  gimbal: NUMBER,
  comms: NUMBER,
  '12v reg': NUMBER,
  '24v reg': NUMBER
};

/** @type {ReceiveType} */
export const safetySwitchType = BOOLEAN;

/** @type {ReceiveType} */
export const sdaType = BOOLEAN;

export const signalStrengthType = {
  signal_strength: NUMBER
};

/** @type {ReceiveType} */
export const throttleType = NUMBER;

/** @Type {ReveiveType} */
export const targetImgType = [{
  topLeft: {lat: NUMBER, lon: NUMBER},
  topRight: {lat: NUMBER, lon: NUMBER},
  bottomLeft: {lat: NUMBER, lon: NUMBER},
  bottomRight: {lat: NUMBER, lon: NUMBER},
  imageUrl: STRING
}];

export const gimbalType = STRING;

/** @type {ReceiveType} */
export const waypointsType = [{
  lat: NUMBER,
  lon: NUMBER,
  alt: NUMBER,
  command: NUMBER
}];

export const sdaWaypointsType = waypointsType;

/** @type {ReceiveType} */
export const windType = {
  windvx: NUMBER,
  windvy: NUMBER,
  windvz: NUMBER
};

/** @type {ReceiveType} */
export const wpDistsType = [NUMBER];

export const coverageType = {
  url: STRING,
  version: NUMBER,
  ext: STRING
};
export const priorityRegionType = {
  high: [{lat: NUMBER, lon: NUMBER}],
  medium: [{lat: NUMBER, lon: NUMBER}],
  low: [{lat: NUMBER, lon: NUMBER}]
};
