// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { BUTTON } from 'js/constants/ButtonTypes';

import ConfirmationButton from 'js/components/General/ConfirmationButton';
import ModeButton from 'js/components/PlaneAction/ModeButton';

import * as StatusActionCreator from 'js/actions/StatusActionCreator';
import { receiveOffAxisTargetEnabled } from 'js/actions/InteropActionCreator';

import { enabledToSuccess } from 'js/utils/ComponentUtils';
import { sendModeSwitch, sendChangeMode, toggleArm, sendRTL, toggleInterop,
         pointToOffAxis, pointToGimbal, toggleSda, toggleDistributed } from 'js/utils/SendApi';
import { PointPropType } from 'js/utils/PropTypes';

function changeMode(type, mode) {
  if (type === 'Mode Switch') {
    sendModeSwitch(mode, () => StatusActionCreator.receiveModeSwitch(mode));
  } else if (type === 'Current Mode') {
    sendChangeMode(mode, () => StatusActionCreator.receiveCurrentMode(mode));
  } else {
    throw 'Invalid Mode';
  }
}

const possible_modes = Object.freeze([
  {name: 'MANUAL', key: 'MANUAL', onClick: changeMode},
  {name: 'AUTO', key: 'AUTO', onClick: changeMode},
  {name: 'AUTOTUNE', key: 'AUTOTUNE', onClick: changeMode},
  {name: 'STABILIZE', key: 'STABILIZE', onClick: changeMode},
  {name: 'LOITER', key: 'LOITER', onClick: changeMode},
  {name: 'RTL', key: 'RTL', onClick: changeMode},
  {name: 'FBWA', key: 'FBWA', onClick: changeMode},
  {name: 'FBWB', key: 'FBWB', onClick: changeMode},
  {name: 'TRAINING', key: 'TRAINING', onClick: changeMode},
  {name: 'CIRCLE', key: 'CIRCLE', onClick: changeMode}
]);

function getStatusButtons(armed) {
  const armText = armed ? 'DISARM' : 'ARM';
  const armColor = enabledToSuccess(armed);
  return [
    {text: armText, color: armColor, type: BUTTON, onClick: () => toggleArm(armed), id: 'TOGGLE_ARM', key: 'TOGGLE_ARM', confirm: true},
    {text: 'Return Home', color: '', type: BUTTON, onClick: sendRTL, id: 'RETURN_HOME', key: 'RETURN_HOME', confirm: false}
  ];
}

function getPlaneModes(mode) {
  return [
    {name: 'Current Mode', modes: possible_modes, value: mode, key: 'CURRENT_MODE', confirm: false}
  ];
}

function getToggleControls(sda_status, active, interop_url, interop_username, interop_password, interop_mission_id, distributed_active, distributed_url, distributedUsername, distributedPassword) {
  return [
    {text: 'Toggle Interop', color: enabledToSuccess(active), type: BUTTON, onClick: () => toggleInterop(active, interop_url, interop_username, interop_password, interop_mission_id), id: 'TOGGLE_INTEROP', key: 'TOGGLE_INTEROP', confirm: false},
    {text: 'Toggle SDA', color: enabledToSuccess(sda_status), type: BUTTON, onClick: () => toggleSda(sda_status), id: 'TOGGLE_SDA', key: 'TOGGLE_SDA', confirm: false},
    {
      text: 'Toggle Distributed', color: enabledToSuccess(distributed_active),
      type: BUTTON, onClick: () => toggleDistributed(distributed_url, distributedUsername, distributedPassword),
      id: 'TOGGLE_DISTRIBUTED', key: 'TOGGLE_DISTRIBUTED', confirm: false
    }
  ];
}

function getGimbalControls(gimbal_status, offaxis_enabled, off_axis, gimbal) {
    const gimbalOffAxisText = offaxis_enabled ? 'IDLE' : 'OFF-AXIS';
    return [
    {text: gimbalOffAxisText + ' Mode', color: enabledToSuccess(offaxis_enabled), type: BUTTON, onClick: () => pointToOffAxis(offaxis_enabled, off_axis.toObject(), () => receiveOffAxisTargetEnabled(!offaxis_enabled)), id: 'POINTER_OFF_AXIS_TARGET', key: 'POINTER_OFF_AXIS_TARGET', confirm: false},
    {text: 'Point To Gimbal Location', color: enabledToSuccess(gimbal_status), type: BUTTON, onClick: () => pointToGimbal(gimbal_status, gimbal.toObject()), id: 'TOGGLE_GIMBAL', key: 'TOGGLE_GIMBAL', confirm: false}
  ];
}

function mapStateToProps({ status: { armed, mode },
    interop: { active, gimbal_status, offaxis_enabled, off_axis, gimbal },
    settings: { interopUrl, interopUsername, interopPassword, interopMissionID, distributedUrl, distributedUsername, distributedPassword },
    sda: { sda_status }, targetImage: { distributed_active } }) {
  return {
    armed, mode, active, gimbal_status, offaxis_enabled, off_axis, 
    gimbal, sda_status, distributed_active, interopUrl, 
    interopUsername, interopPassword, interopMissionID, distributedUrl, distributedUsername, distributedPassword
  }
}

type BtnType = {text: string, color: string, type: string, onClick: Function, id: string, key: string, confirm: boolean};

function createButton(btn: BtnType, lighten: boolean) {
  var btnclass = `btn ${btn.color}${lighten ? ' lighten-1' : ''}`;
  const button = (
    <div key={btn.text} style={{paddingLeft: '5px', paddingRight: '5px', width: '100%'}}>
      <button className={btnclass} onClick={btn.confirm ? () => 0 : btn.onClick} style={{width: '100%'}}>
        {btn.text}
      </button>
    </div>
  );
  if (!btn.confirm)
    return button;
  return (
    <ConfirmationButton
      key={btn.key}
      name={`Are you sure you want to ${btn.text.toLowerCase()} the plane?`}
      onConfirm={btn.onClick}
      onCancel={() => false}
      confirmation_text='Make sure no one is near the plane.'>
      {button}
    </ConfirmationButton>
  );
}

function PlaneActionSection({ armed, mode, active, gimbal_status,
    offaxis_enabled, off_axis, gimbal, sda_status, distributed_active, interopUrl,
    interopUsername, interopPassword, interopMissionID, distributedUrl, distributedUsername, distributedPassword }) {

  const statusButtons = getStatusButtons(armed);
  const planeModes = getPlaneModes(mode);
  const gimbalButtons = getGimbalControls(gimbal_status, offaxis_enabled, off_axis, gimbal);
  const toggleButtons = getToggleControls(sda_status, active, interopUrl, interopUsername, interopPassword, interopMissionID, distributed_active, distributedUrl, distributedUsername, distributedPassword);

  return (
    <div key='plane-action'>
      {statusButtons.map(b => createButton(b, true))}
      {planeModes.map(mode => <ModeButton {...mode} />)}
      {gimbalButtons.map(b => createButton(b, true))}
    </div>
  );
}

PlaneActionSection.propTypes = {
  armed: PropTypes.bool.isRequired,
  mode: PropTypes.string.isRequired,
  active: PropTypes.bool.isRequired,
  gimbal_status: PropTypes.bool.isRequired,
  offaxis_enabled: PropTypes.bool.isRequired,
  off_axis: PointPropType.isRequired,
  gimbal: PointPropType.isRequired,
  sda_status: PropTypes.bool.isRequired,
  distributed_active: PropTypes.bool.isRequired
};

export default connect(mapStateToProps)(PlaneActionSection);
