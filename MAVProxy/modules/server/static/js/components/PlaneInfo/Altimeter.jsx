import React from 'react';
import { connect } from 'react-redux';

import GlobalStore from 'js/stores/GlobalStore';
import { loadNextGauge } from 'js/actions/SettingsActionCreator';

import { redraw, initializeAltimeter, waypointsAreEqual } from 'js/utils/AltimeterUtils';

function mapStateToProps({status: {gps, attitude, mode}, waypoints: {waypoints, current_waypoint}}) {
  return {gps, attitude, mode, waypoints, current_waypoint};
}

let intialized = false;

class Altimeter extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    initializeAltimeter(loadNextGauge);
    this._update(true);
  }

  _update(force = false) {
    redraw(this.props.gps, this.props.attitude,
      this.props.mode, this.props.waypoints, 
      this.props.current_waypoint, force);
    
  }

  render() {
    if (intialized) this._update();
    intialized = true;
    return (
      <div id="altimeter_container" style={{width: '100%', height: '250px'}}>
      </div>
    );
  }
}


export default connect(mapStateToProps)(Altimeter);
