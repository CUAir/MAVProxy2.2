// @flow

import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import WaypointList from 'js/components/Waypoints/WaypointList';
import WaypointControlSection from 'js/components/Waypoints/WaypointControlSection';

import { updateItemSda, updateItem } from 'js/actions/WaypointActionCreator';

const numberStyle = {textAlign: 'left', width: '5%'};
const typeStyle = {textAlign: 'center', width: '25%'};
const cellStyle = {textAlign: 'right'};
const lonStyle = {textAlign: 'center'};

function mapStateToProps({ settings: { unit_switch, sdaMode }, 
    waypoints: { waypoints: wps, sda_waypoints, current_waypoint, show_all_sda, sda_start, sda_end } }) {
  return {
    waypoints: wps,
    sda_waypoints: sda_waypoints,
    unitSwitch: unit_switch,
    baseAltitude: wps.size > 0 ? wps.get(0).alt : 0,
    sdaMode: sdaMode,
    current: current_waypoint,
    showAllSda: show_all_sda,
    sdaStart: sda_start,
    sdaEnd: sda_end
  };
}

type WaypointContainerType = {waypoints: any, sda_waypoints: any, unitSwitch: boolean,
  baseAltitude: number, sdaMode: boolean, current: number, showAllSda: boolean,
  sdaStart: number, sdaEnd: number};
function WaypointContainer({ waypoints, sda_waypoints, unitSwitch, baseAltitude,
    sdaMode, current, showAllSda, sdaStart, sdaEnd }: WaypointContainerType) {
  let wps;
  if (sdaMode && showAllSda && sdaStart !== -1 && sdaEnd !== -1) {
    wps = waypoints.slice(0, sdaStart + 1)
      .concat(sda_waypoints)
      .concat(waypoints.slice(sdaEnd));
  } else if (sdaMode && !showAllSda) {
    wps = sda_waypoints;
  } else {
    wps = waypoints;
  }
  const reorder = sdaMode ? updateItemSda : updateItem;

  return (
    <div>
      <ul id='wp-slide-out' className='side-nav fixed right-aligned'>
        <WaypointList
          baseAltitude={baseAltitude}
          units={unitSwitch}
          wps={wps}
          reorder={reorder}
          sda={sdaMode}
          current={current} />
        <WaypointControlSection />
      </ul>
    </div> 
  );
}

WaypointContainer.propTypes = {
  waypoints: PropTypes.any.isRequired,
  sda_waypoints: PropTypes.any.isRequired,
  unitSwitch: PropTypes.bool.isRequired,
  baseAltitude: PropTypes.number.isRequired,
  sdaMode: PropTypes.bool.isRequired,
  current: PropTypes.number.isRequired,
  showAllSda: PropTypes.bool.isRequired,
  sdaStart: PropTypes.number.isRequired,
  sdaEnd: PropTypes.number.isRequired
};

export default connect(mapStateToProps)(WaypointContainer);
