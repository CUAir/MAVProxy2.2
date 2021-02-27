import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import $ from 'jquery';
import _ from 'lodash'; 

import { decround, rad_to_deg, mToFt, m_sToKnots } from 'js/utils/ComponentUtils';

import { loadNextGauge } from 'js/actions/SettingsActionCreator';

function mapStateToProps({status: { gps, airspeed, attitude, climb_rate, gauge_type } }) {
  return { gps, airspeed, attitude, climb_rate, gauge_type };
}

class Gauage extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.flightIndicator = $.flightIndicator('#flightIndicator', 'attitude', {
      showBox: false, size: 250, img_directory : 'img/instruments/'
    });
  }

  componentWillUpdate() {
    this.flightIndicator = $.flightIndicator('#flightIndicator', this.props.gauge_type, {
        showBox: false, size: 250, img_directory : 'img/instruments/'
    }); 
  }

  render() {
    const { gauge_type, airspeed, attitude: {roll, pitch, yaw}, climb_rate, gps: {rel_alt} } = this.props;
    
    if (this.flightIndicator !== null && this.flightIndicator !== undefined && !_.isEmpty(this.flightIndicator)){
      this.flightIndicator.setRoll(decround(rad_to_deg(-this.props.attitude.roll), 2));
      this.flightIndicator.setPitch(decround(rad_to_deg(this.props.attitude.pitch), 2));
      this.flightIndicator.setHeading(decround(rad_to_deg(this.props.attitude.yaw), 2));   
      this.flightIndicator.setVario(decround(mToFt(this.props.climb_rate) * 60, 3));
      this.flightIndicator.setAirSpeed(decround(m_sToKnots(this.props.airspeed.speed), 3));   
      this.flightIndicator.setAltitude(decround(mToFt(this.props.gps.rel_alt), 3));
    }
    

    return (
      <div onClick={loadNextGauge} className='pointer' 
          style={{height: '250px', paddingLeft: '25px'}}>
          <span id='flightIndicator'></span>
      </div>);
  }
}


export default connect(mapStateToProps)(Gauage);
