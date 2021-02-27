// @flow

import { Record, List } from 'immutable';

import { updateFlight } from 'js/actions/StatusActionCreator';

import { pythagorean } from 'js/utils/ComponentUtils';
import type { StatusAction } from 'js/utils/Actions';

setInterval(updateFlight, 1000);

const Airspeed = Record({airvx: 0, airvy: 0, airvz: 0, speed: 0, climb: 0});
const Attitude = Record({pitch: 0, roll: 0, yaw: 0, pitchspeed: 0, rollspeed: 0, yawspeed: 0});
const GPS = Record({lat: 0, lon: 0, rel_alt: 0, ground_speed: 0, groundvx: 0, groundvy: 0, groundvz: 0, heading: 0});
const Wind = Record({windvx: 0, windvy: 0, windvz: 0, wind_speed: 0});
const Battery = Record({batteryvoltage: 0, batterypct: 0});
const Powerboard = Record({csbatt: 0, nuc: 0, gimbal: 0, comms: 0, '12v reg': 0, '24v reg': 0});
const Link = Record({packet_loss: 0, num: 0, device: '', num_lost: 0, link_delay: 0, device_name: '', alive: false});

function load_next_guage(current_gauge) {
  const gauges = ['altimeter-graph', 'attitude', 'airspeed', 'heading', 'altimeter'];
  const next_index = (gauges.indexOf(current_gauge) + 1) % gauges.length;
  return gauges[next_index];
}

const StatusState = Record({
  airspeed: new Airspeed(),
  climb_rate: 0,
  attitude: new Attitude(),
  gps: new GPS(),
  wind: new Wind(),
  armed: false,
  safety_switch: false,
  gps_link: false,
  plane_link: false,
  gps_status: 0,
  signal_strength: 0,
  battery: new Battery(),
  powerboard: new Powerboard(),
  throttle: 0,
  mode: 'MANUAL',
  mode_switch: 'MANUAL',
  connected: true,
  throttle100: false,
  links: List(),
  manual_time: 0,
  flight_start: 0,
  flight_length: 0,
  in_flight: false,
  manual_start_time: 0,
  existing_manual: 0,
  old_manual: false,
  time_to_land: 0,
  show_ttl: false,
  mission_percent: 0,
  gauge_type: 'altimeter-graph'
});

const initialState = new StatusState();

export default function statusReducer(state: any = initialState, action: StatusAction) {
  switch (action.type) {
  case 'LOAD_NEXT_GAUGE':
    return state.set('gauge_type', load_next_guage(state.gauge_type));
  case 'RECEIVE_AIRSPEED':
    return state
      .set('airspeed', Airspeed(action.airspeed));
  case 'RECEIVE_CLIMB_RATE':
    return state
      .set('climb_rate', action.climb_rate);
  case 'RECEIVE_ATTITUDE':
    return state
      .set('attitude', Attitude(action.attitude));
  case 'RECEIVE_GPS': {
    const { gps } = action;
    const { groundvx, groundvy, groundvz } = gps;
    return state
      .set('gps', GPS(gps))
      .setIn(['gps', 'ground_speed'], pythagorean(groundvx, groundvy, groundvz));
  }
  case 'RECEIVE_WIND': {
    const { wind } = action;
    const { windvx, windvy, windvz } = wind;
    return state
      .set('wind', Wind(wind))
      .setIn(['wind', 'wind_speed'], pythagorean(windvx, windvy, windvz));
  }
  case 'RECEIVE_GPS_STATUS':
    return state
      .set('gps_status', action.gps_status);
  case 'RECEIVE_SIGNAL_STRENGTH':
    return state
      .set('signal_strength', action.signal_strength);
  case 'RECEIVE_ARMED':
    return state
      .set('armed', action.armed);
  case 'RECEIVE_SAFETY_SWITCH':
    return state
      .set('safety_switch', action.safety_switch);
  case 'RECEIVE_GPS_LINK':
    return state
      .set('gps_link', action.gps_link);
  case 'RECEIVE_PLANE_LINK':
    return state
      .set('plane_link', action.plane_link);
  case 'RECEIVE_LINK_DETAILS':
    return state
      .set('links', List(action.links).map(Link));
  case 'RECEIVE_BATTERY':
    return state
      .set('battery', Battery(action.battery));
  case 'RECEIVE_POWERBOARD':
    return state
      .set('powerboard', Powerboard(action.powerboard));
  case 'RECEIVE_THROTTLE':
    return state
      .set('throttle', action.throttle)
      .set('throttle100', state.throttle100 || action.throttle >= 90);
  case 'RECEIVE_CURRENT_MODE':
    return state
      .set('mode', action.mode);
  case 'RECEIVE_MODE_SWITCH':
    return state
      .set('mode_switch', action.mode_switch);
  case 'RECEIVE_TIME_TO_LAND':
    return state
      .set('time_to_land', action.ttl);
  case 'RECEIVE_MISSION_PERCENT':
    return state
      .set('mission_percent', action.mission_percent);
  case 'TOGGLE_SHOW_TTL':
    return state
      .set('show_ttl', !state.get('show_ttl'));
  case 'LOST_CONNECTION':
    return state
      .set('airspeed', new Airspeed())
      .set('climb_rate', 0)
      .set('attitude', new Attitude())
      .set('gps', new GPS())
      .set('wind', new Wind())
      .set('armed', false)
      .set('gps_link', false)
      .set('plane_link', false)
      .set('gps_status', 0)
      .set('signal_strength', 0)
      .set('safety_switch', false)
      .set('battery', new Battery())
      .set('powerboard', new Powerboard())
      .set('throttle', 0)
      .set('mode', 'MANUAL')
      .set('mode_switch', 'MANUAL')
      .set('links', List())
      .set('connected', false);
  case 'GAINED_CONNECTION':
    return state
      .set('connected', true);
  case 'START_FLIGHT': {
    const old_manual = state.mode === 'MANUAL';
    return state
      .set('flight_length', 0)
      .set('manual_time', 0)
      .set('existing_manual', 0)
      .set('flight_start', (new Date).getTime())
      .set('in_flight', true)
      .set('old_manual', old_manual)
      .set('manual_start_time', old_manual ? (new Date).getTime() : 0);
  }
  case 'STOP_FLIGHT':
    return state
      .set('in_flight', false);
  case 'UPDATE_FLIGHT': {
    const { in_flight, flight_start, old_manual, mode } = state;
    let { flight_length, existing_manual, manual_start_time, manual_time } = state;

    if (in_flight) flight_length = (((new Date).getTime()) - flight_start) / 1000;

    if (old_manual && in_flight && mode === 'MANUAL') {
      manual_time = existing_manual + ((new Date).getTime() - manual_start_time) / 1000;
    } else if (old_manual && in_flight) {
      existing_manual += ((new Date).getTime() - manual_start_time) / 1000;
    } else if (in_flight && mode == 'MANUAL') {
      manual_start_time = (new Date).getTime();
      manual_time = existing_manual + ((new Date).getTime() - manual_start_time) / 1000;
    }

    return state
      .set('flight_length', flight_length)
      .set('existing_manual', existing_manual)
      .set('manual_start_time', manual_start_time)
      .set('manual_time', manual_time);
  }
  default:
    return state;
  }
}
