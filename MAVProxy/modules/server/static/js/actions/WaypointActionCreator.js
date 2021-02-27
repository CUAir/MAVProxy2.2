// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { PathSelectionType, WaypointType, PointType } from 'js/utils/Objects';

/**
 * @module actions/WaypointActionCreator
 */

/**
 * Updates a waypoint
 * @param {number} start
 * @param {number} end
 * @returns {undefined}
 */
export function updateItem(start: number, end: number): void {
  return GlobalStore.dispatch({
    type: 'REORDER_WAYPOINTS',
    start, end
  });
}

export function updateItemSda(start: number, end: number): void {
  return GlobalStore.dispatch({
    type: 'REORDER_WAYPOINTS_SDA',
    start, end
  });
}

/**
 * Updates a cell of a waypoint to a new value
 * @param {number} index
 * @param {string} key
 * @param {NValue} newValue
 * @returns {undefined}
 */
export function cellChange(index: number, key: string, newValue: number, sda: boolean): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_UPDATE_CELL',
    index, key, newValue, sda
  });
}

/**
 * Updates the lat and lon of a waypoint
 * @param {number} index
 * @param {number} lat
 * @param {number} lon
 * @returns {undefined}
 */
export function updateCellLatLon(index: number, lat: number, lon: number, sda: boolean): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_UPDATE_CELL_LAT_LON',
    index, lat, lon, sda
  });
}

/**
 * Confirms that the user wanted to click on the waypoint in the list
 * Warns if waypoint is already sent (changes are immediately pushed)
 * @param {number} index
 * @param {Function} onYes - callback function to happen when user presses okay
 * @param {Function} onNo - callback function to happen when user presses cancel
 * @returns {undefined}
 */
export function confirmSelect(index: number, sda: boolean, onYes: Function, onNo: Function): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_CONFIRM_SELECT',
    index, sda, onYes, onNo
  });
}

/**
 * Confirms that the user wanted to click on the waypoint in the map
 * Warns if waypoint is already sent (changes are immediately pushed)
 * @param {number} index - index of waypoint in list
 * @returns {undefined}
 */
export function confirmSelectMap(index: number, sda: boolean): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_CONFIRM_SELECT_MAP',
    index, sda
  });
}

/**
 * Sets the waypoint as selected
 * @param {number} number
 * @returns {undefined}
 */
export function setSelected(number: number): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SET_SELECTED',
    number
  });
}

/**
 * Sets a list of waypoints as selected
 * @param {number} number
 * @returns {undefined}
 */
export function setSelectedList(area): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_LIST_SET_SELECTED',
    area
  });
}

export function clearSelected(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_LIST_CLEAR_SELECTED'
  });
}

/**
 * Increment selected waypoint
 * @param {is_sda} boolean
 * @returns {undefined}
 */
export function incSelected(is_sda: boolean = false): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_INC_SELECTED',
    is_sda
  });
}

/**
 * Decrement selected waypoint
 * @param {is_sda} boolean
 * @returns {undefined}
 */
export function decSelected(is_sda: boolean = false): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_DEC_SELECTED',
    is_sda
  });
}

/**
 * Sets the sda waypoint as selected
 * @param {number} number
 * @returns {undefined}
 */
export function setSelectedSda(number: number): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SET_SELECTED_SDA',
    number
  });
}

/**
 * Adds a temporary waypoint
 * @param {number} lat
 * @param {number} lon
 * @returns {undefined}
 */
export function addWaypoint(lat: number, lon: number): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_ADD',
    lat, lon
  });
}

/**
 * Sends the selected waypoint to the server
 * @returns {undefined}
 */
export function sendWaypoint(quiet: boolean = false): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SEND',
    quiet
  });
}

export function sendAllSdaWaypoints(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SEND_ALL_SDA'
  });
}

/**
 * Deletes the selected waypoint
 * @returns {undefined}
 */
export function deleteWaypoint(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_DELETE'
  });
}

/**
 * Deletes the all SDA waypoints
 * @returns {undefined}
 */
export function deleteAllSdaWaypoints(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_DELETE_ALL_SDA'
  });
}

/**
 * Sets the selected waypoint as current
 * @returns {undefined}
 */
export function setCurrent(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SET_CURRENT'
  });
}

/**
* Loads waypoints from file
* @param {Waypoint[]} wps
* @returns {undefined}
*/
export function loadWaypointsFromFile(wps: WaypointType[]): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINTS_LOAD_FROM_FILE',
    wps
  });
}

/**
* Loads waypoints from competition server
* @param {Waypoint[]} wps
* @returns {undefined}
*/
export function receiveCompetitionWaypoints(waypoints: WaypointType[]): void {
  return GlobalStore.dispatch({
    type: 'COMPETITION_WAYPOINTS_RECEIVE',
    waypoints
  });
}

/**
 * Sets the waypoints to the new batch of received waypoints
 * @param {Waypoint[]} waypoints
 * @returns {undefined}
 */
export function receiveWaypoints(waypoints: WaypointType[]): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINTS_RECEIVE',
    waypoints
  });
}

export function receiveSdaWaypoints(waypoints: WaypointType[]): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINTS_RECEIVE_SDA',
    waypoints
  });
}

/**
 * Sets the received sda suggestion path selection as selection
 * @param {PathSelection} selection
 * @returns {undefined}
 */
export function receiveSdaSelection(selection: PathSelectionType): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINTS_RECEIVE_PATH',
    selection
  });
}

/**
 * Sets the received waypoint number as current
 * @param {number} current
 * @returns {undefined}
 */
export function receiveCurrent(current: number): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINTS_RECEIVE_CURRENT',
    current
  });
}

export function sendAllWaypoints(): void {
  return GlobalStore.dispatch({
    type: 'WAYPOINT_SEND_ALL'
  });
}

export function changeShowSda(show: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_SHOW_SDA',
    show
  });
}

/**
 * Set whether or not map is tracking plane
 * @param {boolean} tracking
 * @returns {undefined}
 */
export function changeIsTracking(tracking: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_TRACKING',
    tracking
  });
}

export function receiveSplines(splines: Object[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SPLINES',
    splines
  });
}

export function receiveCoveragePoints(points: Object[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_COVERAGE_POINTS',
    points
  });
}

export function clearTempWaypoints(): void {
  return GlobalStore.dispatch({
    type: 'CLEAR_TEMP_WPS'
  });
}
