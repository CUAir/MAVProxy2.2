// @flow

import keyMirror from 'keymirror';

/**
 * @module constants/ActionTypes
 */

/** @type {Object<string>} */
export const StatusTypes = Object.freeze(keyMirror({
  RECEIVE_STATUS: null,
  RECEIVE_AIRSPEED: null,
  RECEIVE_CLIMB_RATE: null,
  RECEIVE_ATTITUDE: null,
  RECEIVE_GPS: null,
  RECEIVE_ARMED: null,
  RECEIVE_SAFETY_SWITCH: null,
  RECEIVE_GPS_LINK: null,
  RECEIVE_PLANE_LINK: null,
  RECEIVE_LINK_DETAILS: null,
  RECEIVE_GPS_STATUS: null,
  RECEIVE_SIGNAL_STRENGTH: null,
  RECEIVE_FLIGHT_TIME: null,
  RECEIVE_BATTERY: null,
  RECEIVE_POWERBOARD: null,
  RECEIVE_THROTTLE: null,
  RECEIVE_WIND: null,
  RECEIVE_CURRENT_MODE: null,
  RECEIVE_MODE_SWITCH: null,
  LOST_CONNECTION: null,
  GAINED_CONNECTION: null,
  START_FLIGHT: null,
  STOP_FLIGHT: null,
  RECEIVE_TTL: null,
  RECEIVE_MISSION_PERCENT: null
}));

/** @type {Object<string>} */
export const InteropTypes = Object.freeze(keyMirror({
  RECEIVE_INTEROP_ACTIVE: null,
  RECEIVE_INTEROP_ALIVE: null,
  RECEIVE_OBSTACLES: null,
  RECEIVE_OFF_AXIS: null,
  RECEIVE_MISSION_WAYPOINTS: null,
  RECEIVE_MISSION_WP_DISTS: null,
  GIBMAL_LOCATION: null,
  RECEIVE_OFFAXISTARGET_ENABLED: null,
  GIMBAL_STATUS: null
}));

/** @type {Object<string>} */
export const SettingsTypes = Object.freeze(keyMirror({
  RECEIVE_LOCATION: null,
  RECEIVE_SCRATCHPAD: null,
  RECEIVE_LOCATIONS: null,
  UNIT_SWITCH: null,
  CHANGE_HISTORICAL_SLIDER: null,
  CHANGE_FUTURE_SLIDER: null,
  CHANGE_DATE: null,
  CHANGE_BATTERY_BEFORE: null,
  CHANGE_BATTERY_AFTER: null,
  SAVE_FLIGHT: null,
  DOWNLOAD_FLIGHTCARD: null,
  CLEAR_FLIGHTS: null,
  CHANGE_WIND: null,
  CHANGE_FLIGHTNOTES: null
}));

/** @type {Object<string>} */
export const WaypointTypes = Object.freeze(keyMirror({
  WAYPOINT_ADD: null,
  WAYPOINT_SEND: null,
  WAYPOINT_SEND_ALL_SDA: null,
  WAYPOINT_DELETE: null,
  WAYPOINT_DELETE_ALL_SDA: null,
  WAYPOINT_UPDATE_CELL_LAT_LON: null,
  WAYPOINT_UPDATE_CELL: null,
  WAYPOINT_SET_SELECTED: null,
  WAYPOINT_LIST_SET_SELECTED: null,
  WAYPOINT_LIST_CLEAR_SELECTED: null,
  WAYPOINT_SET_CURRENT: null,
  WAYPOINT_CONFIRM_SELECT: null,
  WAYPOINT_CONFIRM_SELECT_MAP: null,
  REORDER_WAYPOINTS: null,
  REORDER_WAYPOINTS_SDA: null,
  WAYPOINTS_RECEIVE_PATH: null,
  WAYPOINTS_RECEIVE: null,
  WAYPOINTS_RECEIVE_CURRENT: null,
  WAYPOINTS_LOAD_FROM_FILE: null,
  COMPETITION_WAYPOINTS_RECEIVE: null,
  WAYPOINT_SEND_ALL: null,
  WAYPOINTS_RECEIVE_SDA: null,
  WAYPOINT_SET_SELECTED_SDA: null,
  WAYPOINT_INC_SELECTED: null,
  WAYPOINT_DEC_SELECTED: null,
  CHANGE_SHOW_SDA: null
}));

/** @type {Object<string>} */
export const ParametersTypes = Object.freeze(keyMirror({
  RECEIVE_SINGLE_PARAMETER: null,
  RECEIVE_MULTIPLE_PARAMETERS: null,
  EDIT_PARAMETER: null,
  SELECT_PARAMETER: null,
  PARAMETER_LOAD_FROM_FILE: null,
  RECEIVE_NOTE: null,
  RECEIVE_SEARCH_FIELD: null,
  RECEIVE_MAX_PARAM_COUNT: null,
  RECEIVE_MODAL_OPEN: null,
  PARAMETER_SAVE_FROM_MODAL: null
}));

/** @type {Object<string>} */
export const MapTypes = Object.freeze(keyMirror({
  MAP_ADD_PATH: null,
  MAP_CLEAR_PATH: null
}));

export const TargImgTypes = Object.freeze(keyMirror({
  RECEIVE_TARGET_IMAGE: null,
  RECEIVE_DISTRIBUTED_ACTIVE: null,
  RECEIVE_ROI: null
}));

/** @type {Object<string>} */
export const CalibrationTypes = Object.freeze(keyMirror({
  ADD_CALIBRATION_LINE: null,
  CLEAR_CALIBRATION: null
}));

/** @type {Object<string>} */
export const FenceTypes = Object.freeze(keyMirror({
  RECEIVE_FENCES_ENABLED: null,
  RECEIVE_FENCE_POINTS: null
}));

/** @type {Object<string>} */
export const SdaTypes = Object.freeze(keyMirror({
  RECEIVE_SDA_ENABLED: null
}));

/** @type {Object<string>} */
export const TuningTypes = Object.freeze(keyMirror({
  NEXT_TUNING_FLIGHT: null,
  PREV_TUNING_FLIGHT: null,
  UPDATE_TUNING_VALUE: null,
  LOCK_TUNING_VALUE: null,
  RESET_TUNING: null
}));
