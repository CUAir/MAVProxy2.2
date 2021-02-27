// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { ObstacleType, PointType } from 'js/utils/Objects';

/**
 * @module actions/InteropActionCreator
 */

/**
 * Relays that the interop server is active (does not say if it is working)
 * @param {boolean} active
 * @returns {undefined}
 */
export function receiveInteropActive(active: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_ACTIVE',
    active
  });
}

/**
 * Relays that the interop server is working
 * @param {boolean} alive
 * @returns {undefined}
 */
export function receiveInteropAlive(alive: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_INTEROP_ALIVE',
    alive
  });
}

/**
 * Sets the obstacle list to the argument
 * @param {Obstacle[]} obstacles
 * @returns {undefined}
 */
export function receiveObstacles(obstacles: ObstacleType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_OBSTACLES',
    obstacles
  });
}


/**
 * Sets the off-axis target coordinates
 * @param {Point} off_axis
 * @returns {undefined}
 */
export function receiveOffAxis(off_axis: PointType): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_OFF_AXIS',
    off_axis
  });
}

/**
 * Sets the mission waypoints distances list to the argument
 * @param {number[]} mission_wp_dists
 * @returns {undefined}
 */
export function receiveMissionWpDists(mission_wp_dists: number[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MISSION_WP_DISTS',
    mission_wp_dists
  });
}

export function gimbalLocation(lat: number, lon: number): void {
  return GlobalStore.dispatch({
    type: 'GIMBAL_LOCATION',
    lat, lon
  });
}

export function gimbalStatus(status: boolean): void {
  return GlobalStore.dispatch({
    type: 'GIMBAL_STATUS',
    status
  });
}

export function receiveOffAxisTargetEnabled(enabled: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_OFFAXISTARGET_ENABLED',
    enabled
  });
}
