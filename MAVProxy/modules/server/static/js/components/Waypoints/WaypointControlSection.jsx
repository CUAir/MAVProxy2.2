import React from 'react';
import { connect } from 'react-redux';

import * as WaypointActionCreator from 'js/actions/WaypointActionCreator';
import * as SendApi from 'js/utils/SendApi';
import * as ReceiveApi from 'js/utils/ReceiveApi';
import { loadWaypointsFromFile } from 'js/utils/LoadApi';
import { saveWaypointsToFile, saveWaypointsToJson } from 'js/utils/DownloadApi';
import { getSdaWaypoints } from 'js/utils/ReceiveApi';
import { addKeyBindings } from 'js/utils/KeyBindings';


addKeyBindings(Object.freeze([
  {keycode: 'down', scope: 'home', action: () => WaypointActionCreator.incSelected(false)},
  {keycode: 'up', scope: 'home', action: () => WaypointActionCreator.decSelected(false)},
  {keycode: 'alt+shift+r', scope: 'home', action: SendApi.refreshWPs},
  {keycode: 'shift+s', scope: 'home', action: WaypointActionCreator.sendAllWaypoints},
  {keycode: 's', scope: 'home', action: WaypointActionCreator.sendWaypoint},
  {keycode: 'c', scope: 'home', action: WaypointActionCreator.setCurrent}
]));

function editSelected(selected) {
  $(`#wp-edit-button-${selected}`).trigger("click");
}

function getWaypointControls(sent_waypoints, current_waypoint, show_all_wps_sda, sda_start, sda_end, sdaMode,
  extension_distance, flight_height, granularity, max_bank, min_coverage, selected_sda, selected_row) {

  addKeyBindings(Object.freeze([
    {keycode: 'ctrl+shift+s', scope: 'home', action: () => saveWaypointsToFile(sent_waypoints.toJS(), current_waypoint)},
    {keycode: 'enter', scope: 'home', action: () => editSelected(sdaMode ? selected_sda : selected_row)}
  ]));

  const requestCompetitionWaypoints = () => ReceiveApi.getCompetitionWaypoints();

  const requestCoveragePoints = () => SendApi.requestCoveragePoints({
    extension_distance: parseFloat(extension_distance),
    flight_height: parseFloat(flight_height),
    granularity: parseFloat(granularity),
    max_bank: parseFloat(max_bank),
    min_coverage: parseFloat(min_coverage)
  });
  const waypoint_controls = [
    {color: 'unknown', half: true, text: 'Refresh', type: 'button', onClick: SendApi.refreshWPs, key: 'ADD_WP'},
    {color: 'red lighten-2', half: true, text: 'Delete', type: 'button', onClick: WaypointActionCreator.deleteWaypoint, key: 'DELETE_WP'},
    {color: 'green lighten-2', half: false, text: 'Set Current to %c', type: 'button', onClick: WaypointActionCreator.setCurrent, key: 'SET_CURRENT_WP'},
    {color: 'unknown', half: true, text: 'Send %c', type: ' button', onClick: WaypointActionCreator.sendWaypoint, key: 'SEND_WP'},
    {color: 'unknown', half: true, text: 'Send All', type: 'button', onClick: WaypointActionCreator.sendAllWaypoints, key: 'SEND_ALL_WP'},
    {color: 'unknown', half: false, 'text': 'Get Coverage WPs', type: 'button', onClick: requestCoveragePoints, key: 'GET_COVERAGE_WPS'},
    {color: 'error', half: false, 'text': 'Clear Temp WPs', type: 'button', onClick:  WaypointActionCreator.clearTempWaypoints, key: 'CLEAR_TEMP_WPS'},
    {color: 'unknown', half: false, text: 'Load From File', type: 'fileInput', id: 'LOAD_WP_FROM_FILE', onClick: loadWaypointsFromFile, key: 'LOAD_WP_FROM_FILE'},
    {color: 'unknown', half: false, text: 'Load Competition WPs', type: 'button', onClick: requestCompetitionWaypoints, key: 'RECEIVE_WPS'},
    {color: 'unknown', half: true, icon: 'download', text: 'APM', type: 'button', onClick: () => saveWaypointsToFile(sent_waypoints.toJS(), current_waypoint), key: 'SAVE_WP_TO_FILE_APM'},
    {color: 'unknown', half: true, icon: 'download', text: 'auvsi', type: 'button', onClick: () => saveWaypointsToJson(sent_waypoints.toJS()), key: 'SAVE_WP_TO_FILE_INTEROP'},
  ];

  const show_wp_color = show_all_wps_sda ? 'red lighten-2' : 'green lighten-2' ;
  const show_wp_text = show_all_wps_sda ? 'Only show SDA WPs' : 'Show All WPs';
  const waypoint_controls_sda = [
    {color: 'red lighten-2', half: false, text: 'Delete', type: 'button', onClick: WaypointActionCreator.deleteWaypoint, key: 'DELETE_WP'},
    {color: 'unknown', half: false, text: 'Send All SDA WPs', type: 'button', onClick: WaypointActionCreator.sendAllSdaWaypoints, key: 'SEND_ALL_WP_SDA'},
    {color: 'green lighten-2', half: false, text: 'Retrieve SDA WPs', type: 'button', onClick: () => getSdaWaypoints(sda_start, sda_end), key: 'RETRIEVE_SDA'},
    {color: 'red lighten-2', half: false, text: 'Clear Temp SDA WPs', type: 'button', onClick: WaypointActionCreator.deleteAllSdaWaypoints, key: 'DELETE_ALL_SDA'},
    {color: show_wp_color, half: false, text: show_wp_text, type: 'button', onClick: () => WaypointActionCreator.changeShowSda(!show_all_wps_sda), key: 'SHOW_ALL_WPS_SDA'}
  ];
  return sdaMode ? waypoint_controls_sda : waypoint_controls;
}

function mapStateToProps({ waypoints: { waypoints: wps, current_waypoint,
    show_all_sda, sda_start, sda_end, selected_row, selected_sda }, settings: { sdaMode, extension_distance, flight_height,
    granularity, max_bank, min_coverage } }) {
  return {
    wps, current_waypoint, show_all_sda, sda_start, sda_end, sdaMode, extension_distance,
    flight_height, granularity, max_bank, min_coverage, selected_row, selected_sda
  };
}

function createButtonGen(selected_waypoint: int) { 
  return (btn: BtnType) => {
    var btnclass = `btn ${btn.color}`;

    const inline = btn.half;
    const wp = selected_waypoint >= 0 ? ("" + selected_waypoint) : "-";
    const button_text = btn.text.replace("%c", wp);
    var icon = (<div />);

    if (btn.icon != null) {
      icon = <i className={`fa fa-${btn.icon}`} aria-hidden='true'></i>
    }

    if (btn.type == 'fileInput') {
      return (
        <div className='file-field' style={{padding: '2px'}} key={btn.key}>
          <div className='btn' style={{width: '100%'}}>
            <span>{button_text}</span>
            <input type='file' accept='.wp' onChange={(e) => {btn.onClick(e); e.target.value = ''}} />
          </div>
          <div className='file-path-wrapper' style={{width: '0px', height: '0px'}}>
            <input className='file-path validate' accept='.wp' type='text' style={{width: '0px', height: '0px'}} />
          </div>
        </div>
      );
    }
    return (
      <div key={button_text} className={inline ? 'inline-bl' : ''} 
        style={{padding: '2px', width: inline ? '50%' : '100%'}}>
        <button className={btnclass} onClick={btn.onClick} style={{width: '100%'}}>
          {icon} {button_text}
        </button>
      </div>
    );
  }
}

function WaypointControlSection({ wps, current_waypoint, show_all_sda, sda_start, selected_row,
    sda_end, sdaMode, extension_distance, flight_height, granularity, max_bank, min_coverage, 
    selected_sda }) {
  const controls = getWaypointControls(wps.filter(wp => !wp.isTemp),
      current_waypoint, show_all_sda, sda_start, sda_end, sdaMode,
      extension_distance, flight_height, granularity, max_bank, min_coverage,
      selected_sda, selected_row );

  const createButton = createButtonGen(selected_row);
  return (
    <div className='wp-controls'>
      {controls.map(item => createButton(item))}
    </div>
  );
}

export default connect(mapStateToProps)(WaypointControlSection);
