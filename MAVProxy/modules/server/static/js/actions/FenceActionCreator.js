// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { PointType } from 'js/utils/Objects';

/**
 * @module actions/FenceActionCreator
 */

/**
 * Changes the geofence points in the store/map
 * Used when loading geofence
 * @param {Point[]} points
 * @returns {undefined}
 */
export function receiveFencePoints(points: PointType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_FENCE_POINTS',
    points
  });
}

/**
 * Changes the fences value in the store/display
 * Used to toggle fences in map
 * @param {boolean} enabled
 * @returns {undefined}
 */
export function receiveFencesEnabled(enabled: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_FENCES_ENABLED',
    enabled
  });
}

export function saveFences(): void {
  return GlobalStore.dispatch({
    type: 'SAVE_FENCES'
  });
}
