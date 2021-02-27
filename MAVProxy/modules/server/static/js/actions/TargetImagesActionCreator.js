// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { TargetImgType, PointType } from 'js/utils/Objects';

/**
 * @module actions/FenceActionCreator
 */

/**
 * Changes the target images in the store/map
 * Used when loading targetImages
 * @param {TargetImg[]} points
 * @returns {undefined}
 */
export function receiveTargetImg(targetImages: TargetImgType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_TARGET_IMAGE',
    targetImages
  });
}

export function distributedActive(active: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_DISTRIBUTED_ACTIVE',
    active
  });
}

export function uploadCoverageFromFile(coverage: PointType[]): void {
  return GlobalStore.dispatch({
    type: 'UPLOAD_COVERAGE',
    coverage
  });
}

export function receiveCoverage(version: number): void {
  GlobalStore.dispatch({
    type: 'RECEIVE_COVERAGE_IMG',
    version
  });
}

export function receivePriorityRegions(priorityRegions: Object): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_PRIORITY_REGIONS',
    priorityRegions
  });
}

export function receiveRoi(roi: Object[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_ROI',
    roi
  });
}

export function receiveADLCTargets(targets: Object[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_ADLC_TARGETS',
    targets
  });
}

export function receiveAirdropLocation(lat: number, lon: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_AIRDROP_LOCATION',
    lat, lon
  });
}
