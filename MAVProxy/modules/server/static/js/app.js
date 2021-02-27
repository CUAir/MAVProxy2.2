import $ from 'jquery';
import jQuery from 'jquery';
// export for others scripts to use
window.$ = $;
window.jQuery = jQuery;

window.Hammer = require('hammerjs'); // eslint-disable-line no-undef
require('./external/jquery.flightindicators.js'); // eslint-disable-line no-undef

require('materialize-css'); // eslint-disable-line no-undef
window.key = require('keymaster'); // eslint-disable-line no-undef

import React from 'react'; // eslint-disable-line no-unused-vars
import ReactDOM from 'react-dom';

import { PLANE_RECEIVE_FREQUENCY, INTEROP_RECEIVE_FREQUENCY } from 'js/constants/Frequency';

import GCS from 'js/components/GCS';

import { startPlaneReceive, startInteropReceive,
  initializeInterop, initializeCoverage } from 'js/utils/ReceiveApi';

ReactDOM.render(<GCS />, document.getElementById('react'));

startPlaneReceive(1000/PLANE_RECEIVE_FREQUENCY);
startInteropReceive(1000/INTEROP_RECEIVE_FREQUENCY);

initializeInterop();
initializeCoverage();
