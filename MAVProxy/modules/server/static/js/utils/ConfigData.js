// 

/**
 * @module utils/ConfigData
 */

/** @type {Object} confignames */
export const configNames = {
  INTEROP_USERNAME: 'interopUsername',
  INTEROP_PASSWORD: 'interopPassword',
  INTEROP_MISSION_ID: 'interopMissionID',
  INTEROP_URL: 'interopUrl',
  OBC_URL: 'obcUrl',
  TOKEN: 'token',
  SCROLL_START: 'scrollStart',
  SCROLL_END: 'scrollEnd',
  DISTRIBUTED_URL: 'distributedUrl',
  SDA_MODE: 'sdaMode'
};

/**
 * Gets config value from localstorage
 * @param {string} name
 * @returns {string}
 */
export function getConfigValue(name) {
  const value = localStorage[name];
  if (typeof value !== 'string') {
    return '';
  } else {
    return value;
  }
}

/**
 * Sets config value from localstorage
 * @param {string} name
 * @param {string} value
 * @returns {undefined}
 */
export function setConfigValue(name, value) {
  localStorage[name] = value;
}

/**
 * Creates token object
 * @returns {undefined}
 */
export function tokenObj() {
  return {token: getConfigValue(configNames.TOKEN)};
}

/**
 * Creates confirm object
 * @returns {undefined}
 */
export function confirmObj() {
  return {token: getConfigValue(configNames.TOKEN), confirm: 'confirm'};
}
