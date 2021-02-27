// @flow

import { createStore, combineReducers } from 'redux';

import CalibrationReducer from 'js/reducers/CalibrationReducer';
import FenceReducer from 'js/reducers/FenceReducer';
import InteropReducer from 'js/reducers/InteropReducer';
import StatusReducer from 'js/reducers/StatusReducer';
import SettingsReducer from 'js/reducers/SettingsReducer';
import SdaReducer from 'js/reducers/SdaReducer';
import TargetImageReducer from 'js/reducers/TargetImageReducer';
import ParametersReducer from 'js/reducers/ParametersReducer';
import WaypointReducer from 'js/reducers/WaypointReducer';

const GlobalReducer = combineReducers({
  calibration: CalibrationReducer,
  fences: FenceReducer,
  interop: InteropReducer,
  status: StatusReducer,
  settings:  SettingsReducer,
  sda: SdaReducer,
  targetImage: TargetImageReducer,
  parameters: ParametersReducer,
  waypoints: WaypointReducer
});

export default createStore(
  GlobalReducer,
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);
