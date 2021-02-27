// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { FlightType } from 'js/utils/Objects';

/**
 * @module actions/SettingsActionCreator
 */

/**
 * Switches to the next gauge.
 * @returns {undefined}
 */
export function loadNextGauge(): void {
  return GlobalStore.dispatch({
    type: 'LOAD_NEXT_GAUGE'
  });
}

/**
 * Changes store of locations options in settings
 * Used to update location options
 * @param {Object[]} locations
 * @returns {undefined}
 */
export function receiveLocations(locations: Object[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_LOCATIONS',
    locations
  });
}

/**
 * Changes whether the unit switch is metric (true) or US customary (false)
 * @param {boolean} value
 * @returns {undefined}
 */
export function unitSwitch(value: boolean): void {
  return GlobalStore.dispatch({
    type: 'UNIT_SWITCH',
    value
  });
}

/**
 * Changes whether the the slider is historical (or current)
 * @param {boolean} value
 * @returns {undefined}
 */
export function changeHistoricalSlider(value: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_HISTORICAL_SLIDER',
    value
  });
}

/**
 * Changes whether the the slider is future (or current)
 * @param {boolean} value
 * @returns {undefined}
 */
export function changeFutureSlider(value: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_FUTURE_SLIDER',
    value
  });
}

/**
 * Changes whether the the slider is visible on the screen
 * @param {boolean} value
 * @returns {undefined}
 */
export function changeSliderVisible(value: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_SLIDER_VISIBLE',
    value
  });
}

/**
 * Changes whether the plane interpolates animation between points
 * Downside is plane is one second behind, upside is that its flight is smooth
 * @param {boolean} value
 * @returns {undefined}
 */
export function changeSmoothAnimation(value: boolean): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_SMOOTH_ANIMATION',
    value
  });
}

export function changeDate(value: number): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_DATE',
    value
  });
}

export function changeBatteryBefore(battery: string, value: number): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_BATTERY_BEFORE',
    battery, value
  });
}

export function changeBatteryAfter(battery: string, value: number): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_BATTERY_AFTER',
    battery, value
  });
}

export function downloadFlights(): void {
  return GlobalStore.dispatch({
    type: 'DOWNLOAD_FLIGHTCARD'
  });
}

export function saveFlight(flight: FlightType): void {
  return GlobalStore.dispatch({
    type: 'SAVE_FLIGHT',
    flight
  });
}

export function clearFlights(): void {
  return GlobalStore.dispatch({
    type: 'CLEAR_FLIGHTS'
  });
}

export function changeWind(wind: string, value: Object): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_WIND',
    wind, value
  });
}

export function changeFlightNotes(flight_notes: Object): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_FLIGHTNOTES',
    flight_notes: flight_notes.nativeEvent.target.value
  });
}

export function changeAirframe(airframe: Object): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_AIRFRAME',
    airframe: airframe.nativeEvent.target.value
  });
}

export function changeSlider(value: number): void {
  return GlobalStore.dispatch({
    type: 'CHANGE_SLIDER',
    value
  });
}

/**
 * Changes the map location value in the store/display 
 * Used to move map
 * @param {string} location
 * @returns {undefined}
 */
export function receiveLocation(location: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_LOCATION',
    location
  });
}

/**
 * Changes the flight notes
 * @param {string} flight_notes
 * @returns {undefined}
 */
export function receiveScratchpad(scratchpad: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SCRATCHPAD',
    scratchpad
  });
}

export function receiveInteropUrl(interopUrl: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_URL',
    interopUrl
  });
}

export function receiveObcUrl(obcUrl: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_OBC_URL',
    obcUrl
  });
}

export function receiveInteropUsername(interopUsername: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_USERNAME',
    interopUsername
  });
}

export function receiveInteropPassword(interopPassword: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_PASSWORD',
    interopPassword
  });
}

export function receiveInteropMissionID(interopMissionID: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_MISSION_ID',
    interopMissionID
  });
}

export function receiveDistributedUrl(distributedUrl: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_DISTRIBUTED_URL',
    distributedUrl
  });
}

export function receiveDistributedUsername(distributedUsername: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_DISTRIBUTED_USERNAME',
    distributedUsername
  });
}

export function receiveDistributedPassword(distributedPassword: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_DISTRIBUTED_PASSWORD',
    distributedPassword
  });
}

export function receiveToken(token: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_TOKEN',
    token
  });
}

export function receiveScrollStart(scrollStart: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SCROLL_START',
    scrollStart
  });
}

export function receiveScrollEnd(scrollEnd: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SCROLL_END',
    scrollEnd
  });
}

export function receiveSdaMode(sdaMode: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SDA_MODE',
    sdaMode
  });
}

export function receiveExtensionDistance(distance: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_EXTENSION_DISTANCE',
    distance
  });
}

export function receiveFlightHeight(flight_height: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_FLIGHT_HEIGHT',
    flight_height
  });
}

export function receiveCoverageGranularity(granularity: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_COVERAGE_GRANULARITY',
    granularity
  });
}

export function receiveMaxBank(bank: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MAX_BANK',
    bank
  });
}

export function receiveMinCoverage(coverage: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MIN_COVERAGE',
    coverage
  });
}
