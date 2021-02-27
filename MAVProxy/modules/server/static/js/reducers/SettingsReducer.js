import $ from 'jquery';
import { List, OrderedMap, Record } from 'immutable';

import { receiveLocation } from 'js/actions/SettingsActionCreator';

import { getHistoricalData, resumeReceiveLoop, haltReceiveLoop } from 'js/utils/ReceiveApi';
import { downloadFlights } from 'js/utils/DownloadApi';
import type { SettingsAction } from 'js/utils/Actions';

const LocationOption = Record({
  name: '',
  onClick: $.noop,
  key: ''
}, 'LocationOption');

const LocationData = Record({
  leftLon: 0,
  imageURL: '',
  bottomLat: 0,
  topLat: 0,
  rightLon: 0
}, 'LocationData');

const Wind = Record({
  speed: '0',
  direction: 'N'
}, 'Wind');

const Battery = Record({
  cell2: 0,
  cell6: 0,
  cell9: 0
}, 'Battery');

const Flight = Record({
  date: 0,
  airframe: 'bixler',
  flightStart: 0,
  windSpeed: '0',
  windDirection: '',
  flightLength: 0,
  batteryBefore: new Battery(),
  batteryAfter: new Battery(),
  waypointCount: 0,
  waypointScore: 0,
  avgDist: 0,
  flightNotes: '',
  manualTime: 0
}, 'Flight');

const initial_location_map = OrderedMap({
  Neno_Airfield: 'Neno Airfield',
  NAS_Pax: 'Nas Pax',
  SFO_Airport: 'SFO Airport',
  Cornell_Campus: 'Cornell Campus',
  Game_Farm: 'Game Farm',
  Earth_Center: 'Earth Center'
});

const initial_location_dataJS = Object.freeze({
  'Game_Farm': {
    'leftLon': -76.4650662435,
    'imageURL': 'img/satellites/Game_Farm_Satellite.png',
    'bottomLat': 42.4333928552,
    'topLat': 42.4536610611,
    'rightLon': -76.4376004232
  },
  'Earth_Center': {
    'leftLon': -0.0274658203125,
    'imageURL': 'img/satellites/Earth_Center_Satellite.png',
    'bottomLat': -0.0274658192606,
    'topLat': 0.0274658192606,
    'rightLon': 0.0274658203125
  },
  'Neno_Airfield': {
    'leftLon': -76.62631841015623,
    'centerLon': -76.6125855,
    'imageURL': 'img/satellites/Neno_Airfield_Satellite.png',
    'rightLon': -76.59885258984373,
    'centerLat': 42.44763,
    'bottomLat': 42.4374957409895,
    'topLat': 42.457762619755364
  },
  'SFO_Airport': {
    'leftLon': 149.158355767,
    'centerLon': 149.165222,
    'imageURL': 'img/satellites/SFO_Airport_Satellite.png',
    'bottomLat': -35.3688493943,
    'centerLat': -35.3632498,
    'topLat': -35.3576502173,
    'rightLon': 149.172088677
  },
  'Cornell_Campus': {
    'leftLon': -76.4950662435,
    'imageURL': 'img/satellites/Cornell_Campus_Satellite.png',
    'bottomLat': 42.4384214463,
    'topLat': 42.4586880256,
    'rightLon': -76.4676004232
  },
  'White_Square': {
    'leftLon': 1,
    'imageURL': 'img/plainWhiteSquare.png',
    'bottomLat': -1,
    'topLat': 1,
    'rightLon': -1
  },
  'NAS_Pax': {
    'leftLon': -76.423871799,
    'imageURL': 'img/satellites/NAS_Pax_Satellite.png',
    'bottomLat': 38.2750531654,
    'topLat': 38.2966119005,
    'rightLon': -76.3964059787
  }
});
const initial_location_data = OrderedMap(Object.entries(initial_location_dataJS).map(([k, v]) => [k, LocationData(v)]));

function locationChange(location: string) {
  return () => receiveLocation(location.replace(/_/g, ' '));
}

const initial_location_optionsJS = Object.freeze([
  {name: 'Neno Airfield', onClick: locationChange('Neno_Airfield'), key: 'NENO'},
  {name: 'PAX River AFB', onClick: locationChange('NAS_Pax'), key: 'PAX'},
  {name: 'SFO Airport', onClick: locationChange('SFO_Airport'), key: 'SFO'},
  {name: 'Cornell Campus', onClick: locationChange('Cornell_Campus'), key: 'CORNELL'},
  {name: 'Earth Center', onClick: locationChange('Earth_Center'), key: 'EARTH_CENTER'},
  {name: 'Game Farm', onClick: locationChange('Game_Farm'), key: 'GAME_FARM'}
]);
const initial_location_options = List(initial_location_optionsJS).map(LocationOption);

function update_location_options(locations) {
  return List(Object.keys(locations).map(name => LocationOption({
    name: name.replace(/_/g, ' '),
    onClick: locationChange(name),
    key: name.toUpperCase()
  })));
}


function sliderOnChange(sliderValue: number, historical_slider: boolean,
    scrollStart: number, scrollEnd: number) {
  const seconds = !historical_slider ? 20*60 : (scrollEnd - scrollStart)/1000;
  const secondsBack = seconds - sliderValue;
  if (secondsBack < 1 && !historical_slider) {
    resumeReceiveLoop();
  } else if (!historical_slider) {
    const now = new Date();
    const selectedDate = now.getTime() - secondsBack * 1000; // in milliseconds UTC
    getHistoricalData(selectedDate);
    haltReceiveLoop();
  } else {
    const end = new Date(scrollEnd);
    const selectedDate = end.getTime() - secondsBack * 1000; // in milliseconds UTC
    getHistoricalData(selectedDate);
    haltReceiveLoop();
  }
}

function fromLocalStorage(key: string, defaultValue, parse = false) {
  if (typeof localStorage[key] === 'string') {
    return parse ? JSON.parse(localStorage[key]) : localStorage[key];
  } else {
    return defaultValue;
  }
}

const SettingsState = Record({
  location: fromLocalStorage('location', 'Neno Airfield'),
  scratchpad: fromLocalStorage('scratchpad', ''),
  interopUrl: fromLocalStorage('interopUrl', ''),
  obcUrl: fromLocalStorage('obcUrl', ''),
  interopUsername: fromLocalStorage('interopUsername', ''),
  interopPassword: fromLocalStorage('interopPassword', ''),
  interopMissionID: fromLocalStorage('interopMissionID', ''),
  distributedUrl: fromLocalStorage('distributedUrl', ''),
  distributedUsername: fromLocalStorage('distributedUsername', 'Autopilot'),
  distributedPassword: fromLocalStorage('distributedPassword', ''),
  token: fromLocalStorage('token', ''),
  scrollStart: fromLocalStorage('scrollStart', (new Date()).getTime() - 20*60*1000, true), // 20 minutes
  scrollEnd: fromLocalStorage('scrollEnd', (new Date()).getTime(), true),
  sdaMode: fromLocalStorage('sdaMode', false, true),
  location_map: initial_location_map,
  location_data: initial_location_data,
  location_options: initial_location_options,
  unit_switch: true,
  historical_slider: false,
  slider_visible: false,
  smooth_animation: false,
  date: (new Date()).getTime(),
  battery_before: new Battery(),
  battery_after: new Battery(),
  wind: new Wind(),
  flight_notes: '',
  airframe: 'bixler',
  flights: typeof localStorage.flights === 'string' ? List(JSON.parse(localStorage.flights)).map(Flight) : List(),
  extension_distance: 20,
  flight_height: 60,
  granularity: 20,
  max_bank: 30,
  min_coverage: 0.7
});

const initialState = new SettingsState();

export default function settingsReducer(state: any = initialState, action: SettingsAction) {
  switch (action.type) {
  case 'RECEIVE_LOCATIONS':
    return state
      .set('location_map', OrderedMap(Object.keys(action.locations).map(name => [name, name.replace(/_/g, ' ')])))
      .set('location_data', OrderedMap(Object.entries(action.locations).map(([k, v]) => [k, LocationData(v)])))
      .set('location_options', update_location_options(action.locations));
  case 'UNIT_SWITCH':
    return state
      .set('unit_switch', action.value);
  case 'CHANGE_HISTORICAL_SLIDER':
    return state
      .set('historical_slider', action.value);
  case 'CHANGE_SLIDER_VISIBLE':
    return state
      .set('slider_visible', action.value);
  case 'CHANGE_SMOOTH_ANIMATION':
    return state
      .set('smooth_animation', action.value);
  case 'CHANGE_SLIDER':
    sliderOnChange(action.value, state.historical_slider, state.scrollStart, state.scrollEnd);
    return state;
  case 'CHANGE_DATE':
    return state
      .set('date', action.value);
  case 'CHANGE_BATTERY_BEFORE':
    return state
      .setIn(['battery_before', action.battery], action.value);
  case 'CHANGE_BATTERY_AFTER':
    return state
      .setIn(['battery_after', action.battery], action.value);
  case 'SAVE_FLIGHT': {
    const flights = state.get('flights').push(Flight(action.flight));
    localStorage['flights'] = JSON.stringify(flights.toJS());
    return state
      .set('flights', flights);
  }
  case 'DOWNLOAD_FLIGHTCARD':
    downloadFlights(state.get('flights').toJS());
    return state;
  case 'CLEAR_FLIGHTS':
    localStorage['flights'] = JSON.stringify([]);
    return state
      .set('flights', List());
  case 'CHANGE_WIND':
    return state
      .setIn(['wind', action.wind], action.value);
  case 'CHANGE_FLIGHTNOTES':
    return state
      .set('flight_notes', action.flight_notes == null ? state.get('flight_notes') : action.flight_notes);
  case 'CHANGE_AIRFRAME':
    return state
      .set('airframe', action.airframe);
  case 'RECEIVE_LOCATION':
    localStorage['location'] = action.location;
    return state
      .set('location', action.location);
  case 'RECEIVE_SCRATCHPAD':
    localStorage['scratchpad'] = action.scratchpad;
    return state
      .set('scratchpad', action.scratchpad);
  case 'RECEIVE_INTEROP_URL':
    localStorage['interopUrl'] = action.interopUrl;
    return state
      .set('interopUrl', action.interopUrl);
  case 'RECEIVE_OBC_URL':
    localStorage['obcUrl'] = action.obcUrl;
    return state
      .set('obcUrl', action.obcUrl);
  case 'RECEIVE_INTEROP_USERNAME':
    localStorage['interopUsername'] = action.interopUsername;
    return state
      .set('interopUsername', action.interopUsername);
  case 'RECEIVE_INTEROP_PASSWORD':
    localStorage['interopPassword'] = action.interopPassword;
    return state
      .set('interopPassword', action.interopPassword);
  case 'RECEIVE_INTEROP_MISSION_ID':
    localStorage['interopMissionID'] = action.interopMissionID;
    return state
      .set('interopMissionID', action.interopMissionID);
  case 'RECEIVE_DISTRIBUTED_URL':
    localStorage['distributedUrl'] = action.distributedUrl;
    return state
      .set('distributedUrl', action.distributedUrl);
  case 'RECEIVE_DISTRIBUTED_USERNAME':
    localStorage['distributedUsername'] = action.distributedUsername;
    return state
      .set('distributedUsername', action.distributedUsername);
  case 'RECEIVE_DISTRIBUTED_PASSWORD':
    localStorage['distributedPassword'] = action.distributedPassword;
    return state
      .set('distributedPassword', action.distributedPassword);
  case 'RECEIVE_TOKEN':
    localStorage['token'] = action.token;
    return state
      .set('token', action.token);
  case 'RECEIVE_SCROLL_START':
    localStorage['scrollStart'] = JSON.stringify(action.scrollStart);
    return state
      .set('scrollStart', action.scrollStart);
  case 'RECEIVE_SCROLL_END':
    localStorage['scrollEnd'] = JSON.stringify(action.scrollEnd);
    return state
      .set('scrollEnd', action.scrollEnd);
  case 'RECEIVE_SDA_MODE':
    localStorage['sdaMode'] = JSON.stringify(action.sdaMode);
    return state
      .set('sdaMode', action.sdaMode);
  case 'RECEIVE_EXTENSION_DISTANCE':
    return state.set('extension_distance', action.distance);
  case 'RECEIVE_FLIGHT_HEIGHT':
    return state.set('flight_height', action.flight_height);
  case 'RECEIVE_COVERAGE_GRANULARITY':
    return state.set('granularity', action.granularity);
  case 'RECEIVE_MAX_BANK':
    return state.set('max_bank', action.bank);
  case 'RECEIVE_MIN_COVERAGE':
    return state.set('min_coverage', action.coverage);
  default:
    return state;
  }
}
