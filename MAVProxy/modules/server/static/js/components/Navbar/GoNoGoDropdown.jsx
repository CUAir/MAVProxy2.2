// 

import React from 'react';
import autobind from 'autobind-decorator';
import _ from 'lodash';
import { connect } from 'react-redux';
import { List } from 'immutable';
import ImmutablePropTypes from 'react-immutable-proptypes';
import PropTypes from 'prop-types';

import FullWidthButton from 'js/components/General/FullWidthButton';

import { valueToColor, colorToButton, valueToColorName } from 'js/utils/ComponentUtils';

/**
 * @module components/Navbar/GoNoGoDropdown
 */

function getGoNoGoStatus(connected, throttle100, mode) {
  return [
    {name: 'Batteries recorded in flight log', key: 'Batteries_recorded', type: 'checkbox', autoCheck: false},
    {name: 'Redo airspeed calibration', key: 'airspeed_calibration', type: 'checkbox', autoCheck: false},
    {name: 'Receiving plane vitals', value: connected, key: 'plane_vitals', type: 'checkbox', autoCheck: true},
    {name: 'Throttle has reached 100%', value: throttle100, key: 'throtte_test', type: 'checkbox', autoCheck: true},
    {name: 'Catapult will not clip box', key: 'CATAPULT_CLIP_BOX', type: 'checkbox', autoCheck: false},
    {name: 'No slack in catapult line', key: 'CATAPULT_SLACK', type: 'checkbox', autoCheck: false},
    {name: 'pilot and spotter recored in flight log', key: 'pilot_and_spotter_recorded', type: 'checkbox', autoCheck: false},
    {name: 'Catapult handlers recorded in flight log', key: 'catapult_handelers_recorded', type: 'checkbox', autoCheck: false},
    {name: 'Timer & video people recorded in flight log', key: 'timer_&_video_recorded', type: 'checkbox', autoCheck: false},
    {name: 'Plane will not lift off catapult prematurely', key: 'no_premature_lift', type: 'checkbox', autoCheck: false},
    {name: 'Transmitter on high', key: 'transmitter_on_high', type: 'checkbox', autoCheck: false},
    {name: 'Catapult pressurized', key: 'catapult_pressurized', type: 'checkbox', autoCheck: false},
    {name: 'Mission brief complete', key: 'mission_brief', type: 'checkbox', autoCheck: false},
    {name: 'Autopilot in auto', value: mode === 'AUTO', key: 'autopilot_in_auto', type: 'checkbox', autoCheck: true},
    {name: 'Surface test', key: 'surface_test', type: 'checkbox', autoCheck: false},
    {name: 'Throttle test',  key: 'throttle_test', type: 'checkbox', autoCheck: false},
    {name: 'Safety pin',  key: 'safety_pin', type: 'checkbox', autoCheck: false},
    {name: 'Capturing images',  key: 'image_capture', type: 'checkbox', autoCheck: false},
    {name: 'Gimbal pointed at the ground',  key: 'gimbal_point_ground', type: 'checkbox', autoCheck: false}
  ];
}

function getGoNoGoInterop(active, alive) {
  return [
    {name: '(if interop is in use) waypoints are set to ASL', key: 'ASL', type: 'checkbox', autoCheck: false},
    {name: 'interop enabled', value: active && alive, key: 'TOGGLE_Interop', type: 'checkbox', autoCheck: true}
  ];
}

function getGoNoGoWaypoints(waypoints, current_waypoint) {
  //if takeoff waypoint, landing waypoint and one other waypoint is present, a valid flightplan exists
  let takeOff = false;
  let landing = false;
  let otherWP = false; 
  const waypointsSetup = waypoints.filter(wp => !wp.isTemp).some(waypoint => {
    if (waypoint.type === 22) takeOff = true;
    else if (waypoint.type === 21) landing = true;
    else otherWP = true;
    
    return takeOff && landing && otherWP;
  });

  const curr = waypoints.get(current_waypoint);
  const currIsTakeoff = curr !== undefined && curr.type === 22;
  const currIsAboveGround = curr !== undefined && curr.alt > 0;
  return [
    {name: 'waypoints are set up', value: waypointsSetup, key: 'waypoints', type: 'checkbox', autoCheck: true},
    {name: 'takeoff waypoint is set to current', value: currIsTakeoff, key: 'takeoff_waypoint_is_current', type: 'checkbox', autoCheck: true},
    {name: 'takeoff waypoint is above ground', value: currIsAboveGround, key: 'takeoff_waypoint_above_ground', type: 'checkbox', autoCheck: true}
  ];
}

function getGoNoGoParameters(param_map) {
  const modeParamsSet = param_map.get('FLTMODE1').value === 10 && param_map.get('FLTMODE2').value === 10 && //auto
                        param_map.get('FLTMODE3').value === 2 && param_map.get('FLTMODE4').value === 2 && //stabilize
                        param_map.get('FLTMODE5').value === 0 && param_map.get('FLTMODE6').value === 0; //manual
  const autoTakeoffParamsSet = param_map.get('TKOFF_THR_DELAY').value === '0' &&
                               param_map.get('TKOFF_THR_MINACC').value === '10';
  return [
      {name: 'flight mode parameters are set', value: modeParamsSet, key: 'flight_mode_params', type: 'checkbox', autoCheck: true},
      {name: 'auto-takeoff parameters configured', value: autoTakeoffParamsSet, key: 'autotakeoff_param', type: 'checkbox', autoCheck: true}
  ];
}

/**
 * Gets state from the interop, parameter, waypoint, and Status stores
 */
function mapStateToProps({ status: { connected, throttle100, mode }, 
    interop: { active, alive }, parameters: { param_map }, 
    waypoints: { waypoints: wps, current_waypoint} }) {
  return {
    connected, throttle100, mode, active, alive, param_map, wps, current_waypoint
  };
}

function buildChecklist({ connected, throttle100, mode, active, alive, param_map, wps, current_waypoint }) {
  const goNoGoInterop = getGoNoGoInterop(active, alive);
  const goNoGoParameters = getGoNoGoParameters(param_map);
  const goNoGoWaypoints = getGoNoGoWaypoints(wps, current_waypoint);
  const goNoGoStatus = getGoNoGoStatus(connected, throttle100, mode);
  return goNoGoInterop.concat(goNoGoParameters, goNoGoWaypoints, goNoGoStatus);
}

const goNoGoOuterStyle = {height: '50px', marginBottom: '0px'};

class GoNoGoDropdown extends React.Component {

  constructor(props) {
    super(props);

    this.checklist_length = buildChecklist(props).length;
    this.state = {checked: List().setSize(this.checklist_length).map(() => false)};
  }

  /**
  * Changes the non auto check boxes when non auto check box at index i is clicked
  * @param {number} i
  */
  @autobind
  _onChangeClick(i) {
    const newCheckedVal = !this.state.checked.get(i);
    const checked = this.state.checked.set(i, newCheckedVal);
    this.setState({ checked });
  }

  /**
  * Creates an auto-check or non auto-check box for an item with index i based on 
  * the autocheck property of the item
  * @param {number} item
  * @param {number} i
  */
  @autobind
  createCheckBox(item, i) {
    const val = item.autoCheck ? item.value : this.state.checked.get(i);
    const { type, autoCheck, name, key } = item;
    return (
      <tr key={key}>
        <td>
          <input disabled={autoCheck} type={type} checked={val} onChange={() => this._onChangeClick(i)} />
        </td>
        <td>{name}</td>
      </tr>
    );
  }

  /**
  * checks if all the boxes are checked
  * returns a boolean representing whether the boxes are all checked
  * @returns {boolean}
  */
  @autobind
  goCheck() {
    return !(buildChecklist(this.props).some((item, i) =>
      !this.state.checked.get(i) || (item.autoCheck && !item.value)
    ));
  }

  @autobind
  _clearStorage() {
    this.setState({checked: List().setSize(this.checklist_length).map(() => false)});
  }

  render() {
    const v = this.goCheck() ? 100: 0;
    const className = `${valueToColor(v)} ${colorToButton(valueToColor(v))}`;
    const color = valueToColorName(v);
    return (
      <li key='GO_NOGO' className={className} id='GO_NOGO' style={goNoGoOuterStyle}>
        <a data-toggle='dropdown' style={{backgroundColor: color, color: 'white'}}>
          GO_NOGO<span className='caret'></span>
        </a>
        <ul className='dropdown-menu' style={{width: '350px', color: 'black'}}>
          <table className='table dropdown-table'><tbody>
            {buildChecklist(this.props).map(this.createCheckBox)}
            <FullWidthButton color='error' onClick={this._clearStorage} text='Clear Checklist' />
          </tbody></table>
        </ul>
      </li>
    );
  }
}

GoNoGoDropdown.propTypes = {
  connected: PropTypes.bool.isRequired,
  throttle100: PropTypes.bool.isRequired,
  mode: PropTypes.string.isRequired,
  active: PropTypes.bool.isRequired,
  alive: PropTypes.bool.isRequired,
  param_map: ImmutablePropTypes.orderedMap,
  wps: PropTypes.any.isRequired,
  current_waypoint: PropTypes.number.isRequired
}

export default connect(mapStateToProps)(GoNoGoDropdown);
