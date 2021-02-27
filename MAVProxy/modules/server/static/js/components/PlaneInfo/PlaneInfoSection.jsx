// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import CanvasGauge from 'canvas-gauges';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import PlaneInfoItem from 'js/components/PlaneInfo/PlaneInfoItem';
import PlaneActionSection from 'js/components/PlaneAction/PlaneActionSection';
import Altimeter from 'js/components/PlaneInfo/Altimeter';
import Gauge from 'js/components/PlaneInfo/Gauge';

import { unitSwitch } from 'js/actions/SettingsActionCreator';

import { GpsPropType, AirspeedPropType, AttitudePropType, WindPropType } from 'js/utils/PropTypes';
import { decround, rad_to_deg, mToFt, m_sToKnots } from 'js/utils/ComponentUtils';

function mapStateToProps({ settings: { unit_switch },
    status: { gps, airspeed, attitude, wind, throttle, climb_rate, gauge_type } }) {
  return {
    unit_switch, gps, airspeed, attitude, wind, throttle, climb_rate, gauge_type
  };
}

function buildPlaneInfo({ gps, airspeed, attitude, wind, throttle, climb_rate }) {
  const speed_digits = 2;
  const angle_digits = 2;
  const coords_digits = 6;
  const other_digits = 2;
  const { rel_alt, ground_speed, lat, lon } = gps;
  const { roll, pitch, yaw } = attitude;
  return [
    {name: 'Rel. Alt.', value: decround(rel_alt, other_digits), unit: 'm', key: 'REL_ALT'},
    {name: 'Ground Speed', value: decround(ground_speed, speed_digits), unit: 'm/s', key: 'GROUND_SPEED'},
    {name: 'Air Speed', value: decround(airspeed.speed, speed_digits), unit: 'm/s', key: 'AIR_SPEED'},
    {name: 'Roll', value: decround(rad_to_deg(roll), angle_digits), unit: '°', key: 'ROLL'},
    {name: 'Pitch', value: decround(rad_to_deg(pitch), angle_digits), unit: '°', key: 'PITCH'},
    {name: 'Yaw', value: decround(rad_to_deg(yaw), angle_digits), unit: '°', key: 'YAW'},
    {name: 'Latitude', value: decround(lat, coords_digits), unit: '°', key: 'LATITUDE'},
    {name: 'Longitude', value: decround(lon, coords_digits), unit: '°', key: 'LONGITUDE'},
    {name: 'Wind Speed', value: decround(wind.wind_speed, speed_digits), unit: 'm/s', key: 'WIND'},
    {name: 'Throttle', value: decround(throttle, other_digits), unit: '%', key: 'THROTTLE'},
    {name: 'Climb Rate', value: decround(climb_rate, speed_digits), unit: 'm/s', key: 'CLIMB_RATE'}
  ];
}

class PlaneInfoSection extends React.Component {

  attitude = {};


  render() {
    const { unit_switch, altitude } = this.props;
    const planeInfo = buildPlaneInfo(this.props);

    const unitSwitchComponent = (
      <div className='switch'>
        <label>
          KIAS
          <input type='checkbox'
            defaultChecked={unit_switch} 
            onChange={(e) => unitSwitch(e.target.checked)} />
          <span className='lever'></span>
          m/s
        </label>
      </div>
    );

    const gauge_component = () => {
      if (this.props.gauge_type == 'altimeter-graph') {
        return (<Altimeter/>)
      }
      return (<Gauge/>);
    }
    return (
      <ul id='vitals' className='side-nav fixed collection with-header'>
        <li className='collection-header' style={{paddingTop: '7px', paddingBottom: '7px'}}>
          <strong>Plane Info</strong>
          <div className='secondary-content'>{unitSwitchComponent}</div>          
        </li>
          {planeInfo.map(item => <PlaneInfoItem unitSwitch={unit_switch} {...item} />)}
        <li>
          {gauge_component()}
        </li>
        <li style={{zIndex: 30, paddingTop: '10px', position: 'relative'}} >
          <PlaneActionSection />
        </li>
      </ul>
    );
    
  }
}

PlaneInfoSection.propTypes = {
  gps: GpsPropType.isRequired,
  airspeed: AirspeedPropType.isRequired,
  attitude: AttitudePropType.isRequired,
  wind: WindPropType.isRequired,
  throttle: PropTypes.number.isRequired,
  climb_rate: PropTypes.number.isRequired,
  unit_switch: PropTypes.bool.isRequired
};

export default connect(mapStateToProps)(PlaneInfoSection);
