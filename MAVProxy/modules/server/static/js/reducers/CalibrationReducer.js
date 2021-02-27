// @flow

import { Record, List } from 'immutable';

import type { CalibrationAction } from 'js/utils/Actions';

const CalibrationState = Record({
  lines: List()
});

const initialState = CalibrationState();

export default function calibrationReducer(state: any = initialState, action: CalibrationAction) {
  switch (action.type) {
  case 'ADD_CALIBRATION_LINE':
    return state
      .set('lines', state.lines.push(action.line));
  case 'CLEAR_CALIBRATION': 
    return state
      .set('lines', List());
  default:
    return state;
  }
}
