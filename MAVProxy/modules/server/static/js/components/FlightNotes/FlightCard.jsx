// @flow

import React from 'react';
import $ from 'jquery';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { changeDate, changeBatteryBefore, changeBatteryAfter, saveFlight,
         downloadFlights, clearFlights, changeWind, changeFlightNotes,
         changeAirframe } from 'js/actions/SettingsActionCreator';
import { startFlight, stopFlight } from 'js/actions/StatusActionCreator';

import { dateToString, time_to_start, time_to_minutes, decround,
         time_to_date } from 'js/utils/ComponentUtils';
import { BatteryPropType } from 'js/utils/PropTypes';

function getAvgDist(waypoints) {
  const dists = waypoints.filter(wp => !wp.get('isTemp')).map(wp => wp.get('min_dist'));
  return dists.size === 0 ? 0 : dists.reduce((acc, cur) => acc + cur, 0) / dists.size;
}

function mapStateToProps({ status: { flight_length, flight_start, in_flight, manual_time}, 
    settings: { battery_before, battery_after, flights, flight_notes, date, airframe, wind }, 
    interop: { waypoint_score }, waypoints: { waypoints: wps, waypoints_completed } }) {
  return {
    avgDist: getAvgDist(wps),
    waypointScore: waypoint_score, 
    waypointCount: waypoints_completed,
    flightLength: flight_length,
    flightStart: flight_start,
    inFlight: in_flight,
    manualTime: manual_time,
    batteryBefore: battery_before,
    batteryAfter: battery_after,
    flights: flights,
    windSpeed: wind.speed,
    windDirection: wind.direction,
    date: date,
    flightNotes: flight_notes,
    airframe: airframe
  };
}

function allowNan(value) {
  return isNaN(value) ? '' : value.toString();
}

function CardInput(name, onChange, value) {
  let id = 'cardinp-' + name.replace(/ /g, '-');
  let def_val = (value == '0') ? '' : value;
  return (
    <div className='col s3 input-field' style={{paddingLeft: '0px'}}>
      <input id={id} type='text' onChange={onChange} defaultValue={def_val}></input>
      <label htmlFor={id}>{name}</label>    
    </div>
  );
}

function buildRow(flight, index) {
  return (
    <tr key={`flightnote-row-${index}`}>
      <td>{time_to_date(flight.date)}</td>
      <td>{flight.airframe}</td>
      <td>{flight.windSpeed}</td>
      <td>{flight.windDirection}</td>
      <td>{time_to_start(flight.flightStart)}</td>
      <td>{time_to_minutes(flight.flightLength)}</td>
      <td>{time_to_minutes(flight.manualTime)}</td>
      <td>{flight.batteryBefore.cell2}%</td>
      <td>{flight.batteryBefore.cell6}%</td>
      <td>{flight.batteryBefore.cell9}%</td>
      <td>{flight.batteryAfter.cell2}%</td>
      <td>{flight.batteryAfter.cell6}%</td>
      <td>{flight.batteryAfter.cell9}%</td>
      <td>{flight.avgDist}</td>
      <td>{flight.waypointCount}</td>
      <td>{flight.waypointScore}</td>
      <td>{flight.flightNotes}</td>
    </tr>
  );
}

function buildTable(flights) {
  if (flights.length === 0) return null;
  return (
    <table className='table'>
      <thead>
        <tr>
          <th>Date</th>
          <th>Airframe</th>
          <th>Wind Speed</th>
          <th>Wind Direction</th>
          <th>Start Time</th>
          <th>Flight Length</th>
          <th>Manual Time</th>
          <th>2-Cell Before</th>
          <th>6-Cell Before</th>
          <th>9-Cell Before</th>
          <th>2-Cell After</th>
          <th>6-Cell After</th>
          <th>9-Cell After</th>
          <th>Avg Min Dist</th>
          <th>Waypoint Count</th>
          <th>Waypoint Score</th>
          <th>Flight Notes</th>
        </tr>
      </thead>
      <tbody>
        {flights.map(buildRow)}
      </tbody>
    </table>
  );
}
class FlightCard extends React.Component {

  componentDidMount(){
    // unfortunately the only way to add the onChanges is here
    $('#flight-date-sel').pickadate();
    $('#flight-date-sel').on('change', (e) => changeDate(Date.parse(e.target.value)));
  }

  render() {
    const { date, airframe, windSpeed, windDirection, batteryBefore, batteryAfter,
      avgDist, waypointCount, waypointScore, flightStart, flightLength,
      flights, manualTime, flightNotes } = this.props;
    return (
      <div>
        <h3>Flight Card</h3>
        <h5>On Arrival</h5>
        <form>
          <div className='row'>
            <div className='col s3 input-field' style={{paddingLeft: '0px'}}>
              <input type='text' id='flight-date-sel' className='datepicker' />
              <label htmlFor='flight-date-sel'>Flight Date</label>      
            </div>
            {CardInput('Airframe', changeAirframe, airframe)}
            {CardInput('Wind Speed', (e) => changeWind('speed', e.nativeEvent.target.value), allowNan(windSpeed))}
            {CardInput('Wind Direction', (e) => changeWind('direction', e.nativeEvent.target.value), windDirection)}
          </div>
        </form>
        <h5>Batteries</h5>
        <form>
          <div className='row'>
            {CardInput('2-cell % before flight', (e) => changeBatteryBefore('cell2', parseInt(e.nativeEvent.target.value)), allowNan(batteryBefore.cell2))}
            {CardInput('6-cell % before flight', (e) => changeBatteryBefore('cell6', parseInt(e.nativeEvent.target.value)), allowNan(batteryBefore.cell6))}
            {CardInput('9-cell % before flight', (e) => changeBatteryBefore('cell9', parseInt(e.nativeEvent.target.value)), allowNan(batteryBefore.cell9))}
          </div>
        </form>
        <form>
          <div className='row'>
            {CardInput('2-cell % after flight', (e) => changeBatteryAfter('cell2', parseInt(e.nativeEvent.target.value)), allowNan(batteryAfter.cell2))}
            {CardInput('6-cell % after flight', (e) => changeBatteryAfter('cell6', parseInt(e.nativeEvent.target.value)), allowNan(batteryAfter.cell6))}
            {CardInput('9-cell % after flight', (e) => changeBatteryAfter('cell9', parseInt(e.nativeEvent.target.value)), allowNan(batteryAfter.cell9))}
          </div>
        </form>
        <div className='row'>
          <div className='col l4 s12'>Avg Min Dist: {decround(avgDist, 1)} m</div>
          <div className='col l4 s12'>Waypoint Count: {waypointCount}</div>
          <div className='col l4 s12'>Waypoint Score: {waypointScore}</div>
        </div>
        <div className='row'>
          <div className='col l4 s12'>Flight Start Time: {time_to_start(flightStart)}</div>
          <div className='col l4 s12'>Flight Length: {time_to_minutes(flightLength)} seconds</div>
          <div className='col l4 s12'>Manual Time: {time_to_minutes(manualTime)} seconds</div>
        </div>

        <span className='flight-notes'>{CardInput('Flight notes', changeFlightNotes, flightNotes)}</span>
        <a className='btn waves-effect waves-light light-marg' onClick={() => saveFlight(this.props)}>Save Flight</a>
        <a className='btn waves-effect waves-light light-marg' onClick={downloadFlights}>Download</a>
        <a className='btn waves-effect waves-light orange lighten-2 light-marg' onClick={clearFlights}>Clear Flights</a>
        {buildTable(flights)}
      </div>
    );
  }
}

FlightCard.propTypes = {
  avgDist: PropTypes.number.isRequired,
  waypointScore: PropTypes.number.isRequired, 
  waypointCount: PropTypes.number.isRequired,
  flightLength: PropTypes.number.isRequired,
  flightStart: PropTypes.number.isRequired,
  inFlight: PropTypes.bool.isRequired,
  manualTime: PropTypes.number.isRequired,
  batteryBefore: BatteryPropType.isRequired,
  batteryAfter: BatteryPropType.isRequired,
  flights: PropTypes.any.isRequired,
  windSpeed: PropTypes.string.isRequired,
  windDirection: PropTypes.string.isRequired,
  date: PropTypes.number.isRequired,
  flightNotes: PropTypes.string.isRequired,
  airframe: PropTypes.string.isRequired
};

export default connect(mapStateToProps)(FlightCard);
