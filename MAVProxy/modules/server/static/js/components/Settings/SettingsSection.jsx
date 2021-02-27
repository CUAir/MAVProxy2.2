// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';

import { TEXT, CRITICAL_BUTTON, DROPDOWN, BUTTON, DATETIME, CHECKBOX, FILE_INPUT } from 'js/constants/ButtonTypes';

import SettingsItem from 'js/components/Settings/SettingsItem';
import LocationAddButton from 'js/components/Settings/LocationAddButton';

import { receiveFencesEnabled, saveFences } from 'js/actions/FenceActionCreator';
import { changeHistoricalSlider, changeFutureSlider, changeSliderVisible, changeSmoothAnimation, receiveScrollStart, receiveScrollEnd,
         receiveInteropUrl, receiveObcUrl, receiveInteropUsername, receiveInteropPassword, receiveInteropMissionID,
         receiveDistributedUrl, receiveToken, receiveSdaMode, receiveLocation,
         receiveExtensionDistance, receiveFlightHeight, receiveCoverageGranularity,
         receiveMaxBank, receiveMinCoverage, receiveDistributedUsername, receiveDistributedPassword } from 'js/actions/SettingsActionCreator';

import { loadFenceFromFile, loadCoverageFromFile } from 'js/utils/LoadApi';
import { reboot, toggleInterop, toggleSda, toggleDistributed } from 'js/utils/SendApi';

function getSettingsControls(token, sdaMode, sda_status, active, interopUrl, interopUsername, interopPassword, interopMissionID, smooth_animation) {
  return [
    {name: 'Auth Token', value: token, key: 'AUTH_TOKEN', type: TEXT, onChange: (e) => receiveToken(e.nativeEvent.target.value)},
    {name: 'SDA Operator', value: sdaMode, key: 'SDA_MODE', type: CHECKBOX, onChange: (e) => receiveSdaMode(e.target.checked)},
    {name: 'SDA Enabled', type: CHECKBOX, onChange: (e) => toggleSda(sda_status), id: 'TOGGLE_SDA', key: 'TOGGLE_SDA', value: sda_status, confirm: true},
    {name: 'Interop Enabled', value: active, type: CHECKBOX, onChange: (e) => toggleInterop(active, interopUrl, interopUsername, interopPassword, interopMissionID), id: 'TOGGLE_INTEROP', key: 'TOGGLE_INTEROP'},
    {name: 'Realistic Display', value: smooth_animation, type: CHECKBOX, onChange: (e) => changeSmoothAnimation(e.target.checked), id: 'TOGGLE_SMOOTH', key: 'TOGGLE_SMOOTH'}
  ];
}

function getLocationControls(location, location_options) {
  return [
    {name: 'Location', value: location, key: 'LOCATION', type: DROPDOWN, options: location_options, onSelect: (loc) => receiveLocation(loc)}
  ];
}

function getSliderControls(slider_visible, historical_slider, scrollStart, scrollEnd) {
  return [
    {name: 'Scroll Start', value: scrollStart, key: 'SCROLL_START', type: DATETIME, onChange: (e) => receiveScrollStart(e)},
    {name: 'Scroll End', value: scrollEnd, key: 'SCROLL_END', type: DATETIME, onChange: (e) => receiveScrollEnd(e)},
    {name: 'Slider Visible', value: slider_visible, key: 'SLIDER_VISIBLE', type: CHECKBOX, onChange: (e) => changeSliderVisible(e.target.checked)},
    {name: 'Historical Times', value: historical_slider, key: 'HISTORICAL_SLIDER', type: CHECKBOX, onChange: (e) => changeHistoricalSlider(e.target.checked)}
  ];
}

function getInteropControls(interopUrl, interopUsername, interopPassword, interopMissionID) {
  return [
    {name: 'Interop URL', value: interopUrl, key: 'URL', type: TEXT, onChange: (e) => receiveInteropUrl(e.nativeEvent.target.value)},
    //{name: 'Mission ID', value: interopMissionID, key: 'ID', type: TEXT},
    {name: 'Interop Username', value: interopUsername, key: 'USERNAME', type: TEXT, onChange: (e) => receiveInteropUsername(e.nativeEvent.target.value)},
    {name: 'Interop Password', value: interopPassword, key: 'PASSWORD', type: TEXT, onChange: (e) => receiveInteropPassword(e.nativeEvent.target.value)},
    {name: 'Interop Mission ID', value: interopMissionID, key: 'MISSION_ID', type: TEXT, onChange: (e) => receiveInteropMissionID(e.nativeEvent.target.value)}
  ];
}

function getDSControls(obcUrl, distributedUrl, distributedUsername, distributedPassword, distributed_active) {
  return [
    {name: 'OBC URL', value: obcUrl, key: 'OBC_URL', type: TEXT, onChange: (e) => receiveObcUrl(e.nativeEvent.target.value)},
    {name: 'Distributed Server URL', value: distributedUrl, key: 'DISTRIBUTED_URL', type: TEXT, onChange: (e) => receiveDistributedUrl(e.nativeEvent.target.value)},
    //{name: 'DS Username', value: distributedUsername, key: 'DISTRIBUTED_USERNAME', type: TEXT, onChange: (e) => receiveDistributedUsername(e.nativeEvent.target.value)},
    {name: 'DS Password', value: distributedPassword, key: 'DISTRIBUTED_PASSWORD', type: TEXT, onChange: (e) => receiveDistributedPassword(e.nativeEvent.target.value)},
    {name: 'Connect to DS', type: BUTTON, onClick: () => toggleDistributed(distributedUrl, distributedUsername, distributedPassword),
     id: 'TOGGLE_DISTRIBUTED', key: 'TOGGLE_DISTRIBUTED'
     } 
  ];
}

function getFenceControls(enabled) {
  return [
    {name: 'Save Geofence', id: 'SAVE_FENCES', key: 'SAVE_FENCES', type: BUTTON, onClick: saveFences},
    {name: 'Load Geofence', id: 'LOAD_FENCES', key: 'LOAD_FENCES', type: FILE_INPUT, onChange: loadFenceFromFile},
    {name: 'Fences', value: enabled, id: 'FENCES', key: 'FENCES', type: CHECKBOX, onChange: (e) => receiveFencesEnabled(e.nativeEvent.target.checked)}
  ];
}

function getCriticalControls() {
  return [
    {name: 'Reboot', id: 'REBOOT', key: 'REBOOT', type: CRITICAL_BUTTON, onClick: reboot}
  ];
}

function getCoverageControls(extension_distance, flight_height, granularity, max_bank, coverage) {
  return [
    {name: 'Coverage Extension Distance', value: extension_distance, id: 'COV_EXT_DIST', key: 'COV_EXT_DIST', type: TEXT, onChange: (e) => receiveExtensionDistance(e.nativeEvent.target.checked)},
    {name: 'Coverage Flight Height', value: flight_height, id: 'COV_FLT_HGHT', key: 'COV_FLT_HGHT', type: TEXT, onChange: (e) => receiveFlightHeight(e.nativeEvent.target.value)},
    {name: 'Coverage Granularity', value: granularity, id: 'COV_GRAN', key: 'COV_GRAN', type: TEXT, onChange: (e) => receiveCoverageGranularity(e.nativeEvent.target.value)},
    {name: 'Coverage Max Bank', value: max_bank, id: 'COV_MAX_BANK', key: 'COV_MAX_BANK', type: TEXT, onChange: (e) => receiveMaxBank(e.nativeEvent.target.value)},
    {name: 'Coverage Minimum Percent', value: coverage, id: 'COV_MIN_PCT', key: 'COV_MIN_PCT', type: TEXT, onChange: (e) => receiveMinCoverage(e.nativeEvent.target.value)},
    {name: 'Load Coverage Boundary', id: 'LOAD_COV_BOUNDARY', key: 'LOAD_COV_BOUNDARY', type: FILE_INPUT, onChange: loadCoverageFromFile}
  ];
}

function mapStateToProps({ settings: { location, location_options, historical_slider, scrollStart,
    scrollEnd, interopUrl, obcUrl, interopUsername, interopPassword, interopMissionID, distributedUrl, distributedUsername, distributedPassword,
    slider_visible, token, sdaMode, smooth_animation }, fences: { enabled }, sda: { sda_status },
    targetImage: { distributed_active }, interop: { active } }) {
  return {
    location, location_options, historical_slider, scrollStart, scrollEnd,
    interopUrl, obcUrl, interopUsername, interopPassword, interopMissionID, distributedUrl, distributedUsername, distributedPassword,
    token, sdaMode, enabled, sda_status, distributed_active, active, slider_visible, smooth_animation
  };
}

function SettingsSection({location, location_options, historical_slider, scrollStart,
    scrollEnd, interopUrl, obcUrl, interopUsername, interopPassword, interopMissionID, distributedUrl,
    distributedUsername, distributedPassword, token, sdaMode, enabled, sda_status,
    distributed_active, active, slider_visible, smooth_animation }) {
  const locations = getLocationControls(location, location_options);
  const settings = getSettingsControls(token, sdaMode, sda_status, active, interopUrl, interopUsername, interopPassword, interopMissionID, smooth_animation);
  const sliders = getSliderControls(slider_visible, historical_slider, scrollStart, scrollEnd);
  const interops = getInteropControls(interopUrl, interopUsername, interopPassword, interopMissionID);
  const ds = getDSControls(obcUrl, distributedUrl, distributedUsername, distributedPassword, distributed_active);
  const fences = getFenceControls(enabled);

  const critical = getCriticalControls();

  return (
    <div className='container'>
        <div className='row'>
          <h3>Settings</h3>
          <h5>All settings save automatically</h5>
        </div>
        <div className='row'>
          {locations.map(SettingsItem)}
          <LocationAddButton />
        </div>
        <div className='row'>
          {settings.map(SettingsItem)}
        </div>
        <div className='row'>
          {sliders.map(SettingsItem)}
        </div>
        <div className='row'>
          {interops.map(SettingsItem)}
        </div>
        <div className='row'>
          {ds.map(SettingsItem)}
        </div>
        <div className='row'>
          {fences.map(SettingsItem)}
        </div>
        <div className='row'>
          {critical.map(SettingsItem)}.
        </div>
    </div>
  );
}

export default connect(mapStateToProps)(SettingsSection);
