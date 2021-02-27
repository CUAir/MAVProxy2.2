// @flow

import { Record, List } from 'immutable';

import type { TargetImageAction } from 'js/utils/Actions';

const Point = Record({
  lat: 0,
  lon: 0
});

const PriorityRegionObject = Record({
  high: List(),
  medium: List(),
  low: List()
});

const Image = Record({
  topLeft: new Point(),
  topRight: new Point(),
  bottomLeft: new Point(),
  bottomRight: new Point(),
  imageUrl: ''
});

function distributedToPoint(pt: {latitude: number, longitude: number}): any {
  //console.log(pt.latitude);
  return Point({lat: pt.latitude, lon: pt.longitude});
}

function toArray(roi) {
  var list = [];
  var lat = 0;
  var lon = 0;
  for (var i=0; i < roi.length; i++) {
    lat = roi[i].gpsLocation.latitude;
    lon = roi[i].gpsLocation.longitude;
    list.push(Point({lat: lat, lon: lon}));
  }

  return list;
}


function parsePriorityRegions(priorityRegions: Object): any {
  return PriorityRegionObject({
    high: List(priorityRegions.high.map(distributedToPoint)),
    medium: List(priorityRegions.medium.map(distributedToPoint)),
    low: List(priorityRegions.low.map(distributedToPoint))
  });
}

const TargetImageState = Record({
  target_images: List(),
  distributed_active: false,
  coverage: List(),
  coverage_version: -1,
  priority_regions: new PriorityRegionObject(),
  roi: List(),
  adlc_targets: List(),
  airdrop_location: new Point()
});

const initialState = new TargetImageState();

export default function TargetImageReducer(state: any = initialState, action: TargetImageAction) {
  switch (action.type) {
  case 'RECEIVE_TARGET_IMAGE':
    return state
      .set('target_images', List(action.targetImages.map(Image)));
  case 'RECEIVE_DISTRIBUTED_ACTIVE':
    return state
      .set('distributed_active', action.active);
  case 'UPLOAD_COVERAGE':
    return state
      .set('coverage', List(action.coverage.map(Point)));
  case 'RECEIVE_COVERAGE_IMG':
    return state
      .set('coverage_version', action.version);
  case 'RECEIVE_PRIORITY_REGIONS':
    return state
    .set('priority_regions', parsePriorityRegions(action.priorityRegions));
  case 'RECEIVE_ROI':
    return state
      .set('roi', toArray(action.roi));
  case 'RECEIVE_ADLC_TARGETS':
    return state
      .set('adlc_targets', List(action.targets.map(distributedToPoint)));
  case 'RECEIVE_AIRDROP_LOCATION':
    return state
      .set('airdrop_location', Point({lat: action.lat, lon: action.lon}));
  default:
    return state;
  }
}
