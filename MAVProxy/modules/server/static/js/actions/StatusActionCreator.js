// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { AirspeedType, AttitudeType, GpsType, WindType, LinkType,
              BatteryType, PowerboardType } from 'js/utils/Objects';

/**
 * @module actions/StatusActionCreator
 */

/**
 * Changes airspeed values
 * @param {Airspeed} airspeed
 * @returns {undefined}
 */
export function receiveAirspeed(airspeed: AirspeedType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_AIRSPEED',
    airspeed
  });
}

/**
 * Changes climb rate
 * @param {number} climb_rate
 * @returns {undefined}
 */
export function receiveClimbRate(climb_rate: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_CLIMB_RATE',
    climb_rate
  });
}

/**
 * Changes attitude values
 * @param {Attitude} attitude
 * @returns {undefined}
 */
export function receiveAttitude(attitude: AttitudeType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_ATTITUDE',
    attitude
  });
}

/**
 * Changes time to landing values
 * @param {number} ttl
 * @returns {undefined}
 */
export function receiveTimeToLanding(ttl: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_TIME_TO_LAND',
    ttl
  });
}

/**
 * Changes wp path coverage percentage value
 * @param {number} mission_percent
 * @returns {undefined}
 */
export function receiveMissionPercent(mission_percent: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MISSION_PERCENT',
    mission_percent
  });
}

export function toggleShowTTL(): void {
  return GlobalStore.dispatch({
    type: 'TOGGLE_SHOW_TTL'
  });
}

/**
 * Changes gps values
 * @param {GPS} gps
 * @returns {undefined}
 */
export function receiveGPS(gps: GpsType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_GPS',
    gps
  });
}

/**
 * Changes GPSStatus values
 * @param {GPSStatus} gps_status
 * @returns {undefined}
 */
export function receiveGPSStatus(gps_status: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_GPS_STATUS',
    gps_status
  });
}

/**
 * Changes SignalStrength values
 * @param {SignalStregth} signal_strength
 * @returns {undefined}
 */
export function receiveSignalStrength(signal_strength: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SIGNAL_STRENGTH',
    signal_strength
  });
}

/**
 * Changes FlightTime values
 * @param {FlightTime} flight_time
 * @returns {undefined}
 */
export function receiveFlightTime(flight_time: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_FLIGHT_TIME',
    flight_time
  });
}

/**
 * Changes wind values
 * @param {Wind} wind
 * @returns {undefined}
 */
export function receiveWind(wind: WindType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_WIND',
    wind
  });
}

/**
 * Changes armed value
 * @param {boolean} armed
 * @returns {undefined}
 */
export function receiveArmed(armed: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_ARMED',
    armed
  });
}

/**
 * Changes safety switch value
 * @param {boolean} safety_switch
 * @returns {undefined}
 */
export function receiveSafetySwitch(safety_switch: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SAFETY_SWITCH',
    safety_switch
  });
}

/**
 * Changes GPS link value
 * @param {boolean} gps_link
 * @returns {undefined}
 */
export function receiveGPSLink(gps_link: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_GPS_LINK',
    gps_link
  });
}

/**
 * Changes plane link value
 * @param {boolean} plane_link
 * @returns {undefined}
 */
export function receivePlaneLink(plane_link: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_PLANE_LINK',
    plane_link
  });
}

export function receiveLinkDetails(links: LinkType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_LINK_DETAILS',
    links
  });
}

/**
 * Changes throttle value
 * @param {number} throttle
 * @returns {undefined}
 */
export function receiveThrottle(throttle: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_THROTTLE',
    throttle
  });
}

/**
 * Changes battery value
 * @param {number} battery
 * @returns {undefined}
 */
export function receiveBattery(battery: BatteryType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_BATTERY',
    battery
  });
}

/**
 * Changes power board values
 * @param {Object} powerboard
 * @returns {undefined}
 */
export function receivePowerboard(powerboard: PowerboardType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_POWERBOARD',
    powerboard
  });
}

/**
 * Changes current mode value
 * @param {string} mode
 * @returns {undefined}
 */
export function receiveCurrentMode(mode: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_CURRENT_MODE',
    mode
  });
}

/**
 * Changes mode switch value
 * @param {string} mode_switch
 * @returns {undefined}
 */
export function receiveModeSwitch(mode_switch: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MODE_SWITCH',
    mode_switch
  });
}

/**
 * Call this when link to backend is lost (API fails)
 * @returns {undefined}
 */
export function disconnect(): void {
  return GlobalStore.dispatch({
    type: 'LOST_CONNECTION'
  });
}

/**
 * Call this when the link to backend is regained (API starts working again)
 * @returns {undefined}
 */
export function reconnect(): void {
  return GlobalStore.dispatch({
    type: 'GAINED_CONNECTION'
  });
}

export function startFlight(): void {
  return GlobalStore.dispatch({
    type: 'START_FLIGHT'
  });
}

export function stopFlight(): void {
  return GlobalStore.dispatch({
    type: 'STOP_FLIGHT'
  });
}

export function updateFlight(): void {
  return GlobalStore.dispatch({
    type: 'UPDATE_FLIGHT'
  });
}
