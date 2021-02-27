// @flow

import { Record, List } from 'immutable';

import type { SdaAction } from 'js/utils/Actions';
import type { PlanePathPointType } from '../utils/Objects';


const SdaState = Record({
  sda_status: false,
  obstacle_paths: List(),
  plane_path: List()
});

const initialState = new SdaState();

function planePathToImmutable(path: PlanePathPointType[]): List<*> {
  return List(path);
}

export default function sdaReducer(state: any = initialState, action: SdaAction) {
  switch (action.type) {
  case 'RECEIVE_SDA_ENABLED':
    return state
      .set('sda_status', action.enabled);
  case 'RECEIVE_PLANE_PATH':
    return state
    .set('plane_path', planePathToImmutable(action.plane_path));
  default:
    return state;
  }
}
