// @flow

import { Record, List } from 'immutable';

import { saveFenceToFile } from 'js/utils/DownloadApi';
import type { FenceAction } from 'js/utils/Actions';

const FencePoint = Record({
  lat: 0,
  lon: 0
});

const FenceState = Record({ 
  points: List(),
  enabled: false
});

const initialState = new FenceState();

export default function FencersReducer(state: any = initialState, action: FenceAction) {
  switch(action.type) {
  case 'RECEIVE_FENCE_POINTS':
    return state
    .set('points', List(action.points).map(FencePoint));
  case 'RECEIVE_FENCES_ENABLED':
    return state
    .set('enabled', action.enabled);
  case 'SAVE_FENCES':
    saveFenceToFile(state.points);
    return state;
  default:
    return state;
  }
}
