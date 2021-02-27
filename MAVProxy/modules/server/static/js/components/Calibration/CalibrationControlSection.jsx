// @flow

import React from 'react';
import autobind from 'autobind-decorator';

import FullWidthElement from 'js/components/General/FullWidthElement';

import { BUTTON } from 'js/constants/ButtonTypes';

import { clearCalibrationLines } from 'js/actions/CalibrationActionCreator';

import { calibrationAStart, calibrationGStart, calibrationPStart, calibrationContinue,
         calibrationRCStart, calibrationRCStop } from 'js/utils/SendApi';

const controls = Object.freeze([
  {color: '', text: 'Start Accelerometer Calibration', type: BUTTON, onClick: calibrationAStart, id: 'CALIBRATION_A_START'},
  {color: '', text: 'Start Gyroscope Calibration', type: BUTTON, onClick: calibrationGStart, id: 'CALIBRATION_G_START'},
  {color: '', text: 'Start Pressure Calibration', type: BUTTON, onClick: calibrationPStart, id: 'CALIBRATION_P_START'},
  {color: '', text: 'Start RC Calibration', type: BUTTON, onClick: calibrationRCStart, id: 'CALIBRATION_RC_START'},
  {color: 'orange lighten-2', text: 'Stop RC Calibration', type: BUTTON, onClick: calibrationRCStop, id: 'CALIBRATION_RC_STOP'},
  {color: 'blue lighten-2', text: 'Continue', type: BUTTON, onClick: calibrationContinue, id: 'CALIBRATION_CONTINUE'},
  {color: 'red lighten-2', text: 'Clear', type: BUTTON, onClick: clearCalibrationLines, id: 'CALIBRATION_CLEAR'}
]);

export default function CalibrationControlSection() {
  return (
    <div className='col s3'>
      {controls.map(FullWidthElement)}
    </div>
  );
}
