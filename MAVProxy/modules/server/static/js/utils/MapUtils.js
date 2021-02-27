import L from 'leaflet';
import Leaflet from 'leaflet';
import 'leaflet-imageoverlay-rotated';
import 'leaflet-rotatedmarker';
import 'leaflet-easybutton';
import 'leaflet-curve';
import 'leaflet-draw';

import _ from 'lodash';

import * as WaypointActionCreator from 'js/actions/WaypointActionCreator';
import * as InteropActionCreator from 'js/actions/InteropActionCreator';
import geolib from 'geolib';
import { mToFt, decround, alert } from 'js/utils/ComponentUtils';
import { getWaypoints } from './ReceiveApi';
import { clearSplines, clearCoverage, simulateCoverage } from 'js/utils/SendApi';
import { PlanePathPointType } from 'js/utils/Objects';
import GlobalStore from '../stores/GlobalStore';
import { receiveCurrent } from '../actions/WaypointActionCreator';

/**
 * @module utils/MapUtils
 */

var map;
// var locationFilter;
let dragging = false;
let rulerActive = false;
let sdaSelectActive = false;
let coverageActive = false;
let rulerStart = null;
let targetImgOnMap = false;
let gimbalActive = false;
var sdaSelectButton;
var zooming = true;
var sda_selection = {};
var current_location = 'Neno_Airfield';
var coverage_img = null;

const ROI_RADIUS = 35;

function setMap() {
  map = L.map('map').setZoom(17);

  var drawPluginOptions = {
    draw: {
      polygon: false,
      polyline: false,
      circle: false,
      marker: false,
      circlemarker: false,
      rectangle: {
        repeatMode: false,
        shapeOptions: {
          color: '#97009c'
        }
      },
    },
  };

  L.drawLocal.draw.toolbar.buttons.rectangle = '';
  L.drawLocal.draw.toolbar.actions = '';
  // L.drawLocal.draw.handlers.rectangle.tooltip.start = '';
  L.drawLocal.draw.handlers.simpleshape.tooltip.end = '';
  console.log(L.drawLocal.draw)

  // Initialise the draw control and pass it the FeatureGroup of editable layers
  var drawControl = new L.Control.Draw(drawPluginOptions);
  map.addControl(drawControl);

  getSelectionBounds();
}

function getSelectionBounds() {
  map.on('draw:created', function (e) {

    var rect = e.layer;
    WaypointActionCreator.clearSelected();
    WaypointActionCreator.setSelectedList(rect);

  });
}

let planeMarker;
let offAxisMarker;
function setMarkers() {
  planeMarker = L.marker([0, 0], {
    icon: planeIcon,
    zIndexOffset: 10,
    rotationAngle: 0,
    rotationOrigin: 'center'
  }).addTo(map);
  offAxisMarker = L.marker([0, 0], { icon: offAxisIcon, zIndexOffset: 10 }).addTo(map);
}

var waypointPath;
var planePath;
var sdaPath;

function setPaths() {
  waypointPath = Leaflet.polyline([], { color: 'red', weight: 8 }).addTo(map);
  planePath = Leaflet.polyline([], { color: 'orange', dashArray: '5,15', weight: 5 }).addTo(map);
  sdaPath = Leaflet.polyline([], { color: 'pink', dashArray: '5,15', weight: 5 }).addTo(map);
}

///////////////Plane Icons//////////////////

const offAxisIconHidden = L.icon({
  iconUrl: './img/markers/offAxisMarker.png',
  iconSize: [1, 1]
});

const planeIconRealistic = L.icon({
  iconUrl: './img/planeGraphics/theia.png',
  iconSize: [80, 80]
});

const planeIconPrediction = L.icon({
  iconUrl: './img/planeGraphics/plane_prediction.png',
  iconSize: [38, 45]
});

const planeIconHidden = L.icon({
  iconUrl: './img/planeGraphics/planeN.png',
  iconSize: [1, 1]
});

const planeIcon = L.icon({
  iconUrl: './img/planeGraphics/planeN.png',
  iconSize: [38, 45]
});

const offAxisIcon = L.icon({
  iconUrl: './img/markers/offAxisMarker.png',
  iconSize: [38, 38]
});

const gimbalIcon = L.icon({
  iconUrl: './img/markers/gimbalMarker.png',
  iconSize: [38, 38]
});

const adlc_icon = L.icon({
  iconUrl: './img/markers/visionMarker.png',
  iconSize: [40, 40]
});

const airdrop_icon = L.icon({
  iconUrl: './img/markers/airdropMarker.png',
  iconSize: [40, 40]
});

var tempMarkerIcon;
var currentMarkerIcon;
var markerIcon;
var alt1MarkerIcon;
var alt2MarkerIcon;
var alt3MarkerIcon;
var alt4MarkerIcon;
var zeroAltMarkerIcon;
var sdaMarkerIcon;
var highlightMarkerIcon;
var _icons = [];

/**
 * Initializes the marker objects
 * @returns {undefined}
 */
function initializeMarkers() {
  var tempMarkerImageURL = 'img/markers/tempWPMarker.png';
  var iconSize = [30, 41];
  var iconAnchor = [15, 41];
  var popupAnchor = [0, -41];
  tempMarkerIcon = Leaflet.icon({
    iconUrl: tempMarkerImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var markerImageURL = 'img/markers/sentWPMarker.png';
  markerIcon = Leaflet.icon({
    iconUrl: markerImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var markerAlt1ImageURL = 'img/markers/alt1WPMarker.png';
  alt1MarkerIcon = Leaflet.icon({
    iconUrl: markerAlt1ImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var markerAlt2ImageURL = 'img/markers/alt2WPMarker.png';
  alt2MarkerIcon = Leaflet.icon({
    iconUrl: markerAlt2ImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var markerAlt3ImageURL = 'img/markers/alt3WPMarker.png';
  alt3MarkerIcon = Leaflet.icon({
    iconUrl: markerAlt3ImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var markerAlt4ImageURL = 'img/markers/alt4WPMarker.png';
  alt4MarkerIcon = Leaflet.icon({
    iconUrl: markerAlt4ImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var zeroAltImageURL = 'img/markers/zeroAltMarker.png';
  zeroAltMarkerIcon = Leaflet.icon({
    iconUrl: zeroAltImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var currentMarkerImageURL = 'img/markers/currentWPMarker.png';
  currentMarkerIcon = Leaflet.icon({
    iconUrl: currentMarkerImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var sdaMarkerImageURL = 'img/markers/sdaWPMarker.png';
  sdaMarkerIcon = Leaflet.icon({
    iconUrl: sdaMarkerImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  var highlightMarkerImageURL = 'img/markers/highlightWPMarker.png';
  highlightMarkerIcon = Leaflet.icon({
    iconUrl: highlightMarkerImageURL,
    iconSize, iconAnchor, popupAnchor
  });

  _icons = [zeroAltMarkerIcon, markerIcon, alt1MarkerIcon, alt2MarkerIcon, alt3MarkerIcon, alt4MarkerIcon];
}

/**
 * Creates a temporary marker on the map
 * @params {Object} e
 * @returns {undefined}
 */
function createTempMarker(e) {
  WaypointActionCreator.addWaypoint(e.latlng.lat, e.latlng.lng);
}

/**
 * Centers the map on the plane's current GPS coordinates
 * @returns {undefined}
 */
let _center_on_plane = false;
function changeCenterOnPlane() {
  _center_on_plane = !_center_on_plane;
  WaypointActionCreator.changeIsTracking(_center_on_plane);
  if (_center_on_plane) centerOnPlane();
}

function centerOnPlane() {
  var latlng = planeMarker.getLatLng();
  map.panTo([latlng.lat, latlng.lng]);
}

/**
 * Starts ruler on map
 * @returns {undefined}
 */
function startRuler() {
  rulerActive = true;
}

function changeTargetImgs() {
  targetImgOnMap = !targetImgOnMap;
  if (!targetImgOnMap) {
    _old_target_img_objects.forEach(removeObj);
    _old_target_img_objects = [];
  }
}

function startGimbal() {
  gimbalActive = true;
}

/**
 * Disables and reenables all zooming other than the + and - buttons
 * @returns {undefined}
 */
function toggleZoom() {
  if (zooming) {
    map.touchZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    zooming = false;
  } else {
    map.touchZoom.enable();
    map.scrollWheelZoom.enable();
    map.boxZoom.enable();
    zooming = true;
  }
}

//Coverage toggle button
function showCoverage() {
  coverageActive = true;
  if (coverage_img != null) {
    coverage_img.addTo(map);
    coverage_img.bringToFront();
  }
}

function hideCoverage() {
  coverageActive = false;
  if (coverage_img != null) {
    removeObj(coverage_img);
  }
}

/**
 * Starts sda select mode on map
 * @returns {undefined}
 */
function startSdaSelect() {
  sdaSelectButton.disable();
  sdaSelectActive = true;
}

/**
 * Starts sda select mode on map
 * @returns {undefined}
 */
function deleteSda() {
  WaypointActionCreator.deleteAllSdaWaypoints();
}

/**
 * Gets the index of a marker object in the array (using the LatLng functionality)
 * @param {LeafletObject[]} array
 * @param {LeafletObject} object
 * @returns {number} index of object
 * @throws Object Not Found if no matching objects found
 */
function listIndex(array, object) {
  var result = -1;
  for (var elt = 0; elt < array.length; elt++) {
    if (array[elt].getLatLng().equals(object.getLatLng())) {
      result = elt;
    }
  }
  if (result === -1) throw 'Object Not Found';
  else return result;
}

/**
 * Handler for sda path selection. dispatches selection to WaypointActionCreator
 * @returns {undefined}
 */
function sdaSelect(e) {
  if (sdaSelectActive) {
    var marker = e.target;
    var object_list = marker._popup._content[0] === 'T' ? _old_temp_waypoint_objects : _old_waypoint_objects;
    var index = listIndex(object_list, marker);
    if (sda_selection.start == undefined) {
      //first waypoint selected
      sda_selection.start = index;
      // Pop up a dialog box
      var buf = prompt('Please enter buffer:', 50);
      if (buf == null || buf == '') {
        sda_selection.buf = 50;
      } else {
        sda_selection.buf = parseInt(buf);
      }
    } else {
      //second waypoint selected
      sda_selection.end = index;
      if (index < sda_selection.start) {
        sda_selection.end = sda_selection.start;
        sda_selection.start = index;
      }
      WaypointActionCreator.receiveSdaSelection(sda_selection);
      sda_selection = {};
      sdaSelectButton.enable();
      sdaSelectActive = false;
    }
  }
}

/**
 * Uses binary search to find the index of the
 * obstacle path point closest to given time
 * @returns {ObstaclePathPoint}
 */
function findClosestTimePoint(points, searchElement: number) {

  var minIndex = 0;
  var maxIndex = points.length - 1;
  var currentIndex;
  var currentElement;

  while (minIndex <= maxIndex) {
    currentIndex = (minIndex + maxIndex) / 2 | 0;
    currentElement = points[currentIndex].time;

    if (currentElement < searchElement) {
      minIndex = currentIndex + 1;
    }
    else if (currentElement > searchElement) {
      maxIndex = currentIndex - 1;
    }
    else {
      return currentIndex;
    }
  }
  return Math.max(maxIndex, 0);
}


//////////////// Plane Path Predictions /////////////////////

var _plane_prediction_path;

export function drawPlanePredictionPath(points: PlanePathPointType[]) {
  if (_plane_prediction_path !== undefined) {
    map.removeLayer(_plane_prediction_path);
  }
  let latlngs = points.map(p => [p.lat, p.lon]);
  var polyline = L.polyline(latlngs).addTo(map);
  _plane_prediction_path = polyline;
}

function _toDeg(rad: number) {
  return rad * 180 / Math.PI;
}


function directionFromCoords(currentLoc: PlanePathPointType, nextLoc: PlanePathPointType) {
  const lat1 = currentLoc.lat,
    lng1 = currentLoc.lon,
    lat2 = nextLoc.lat,
    lng2 = nextLoc.lon;

  const dLon = (lng2 - lng1);
  const y = Math.sin(dLon) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  const brng = _toDeg(Math.atan2(y, x));
  return 360 - ((brng + 360) % 360);
}

let planePredictionMarker;
export function updatePlanePredictionMarker(resetTime: number, offsetTime: number) { // eslint-disable-line no-unused-vars
  const { sda } = GlobalStore.getState();
  const path_prediction = sda.plane_path.toJS();
  if (path_prediction.length > 0) {
    // if the path contains more than one point, add or update plane marker on map
    const index = findClosestTimePoint(path_prediction, resetTime + offsetTime);
    const latlng = path_prediction[index];
    var angle = 0;
    if (planePredictionMarker == null) {
      if (path_prediction.length > 1) {
        angle = directionFromCoords(path_prediction[0], path_prediction[1]);
      }
      planePredictionMarker = L.marker(latlng, {
        icon: planeIconPrediction,
        zIndexOffset: 9,
        rotationAngle: angle,
        rotationOrigin: 'center'
      }).addTo(map);
    } else {
      if (index + 1 < path_prediction.length) {
        // if there are two points left, use them to calculate the current heading direction
        angle = directionFromCoords(path_prediction[index], path_prediction[index + 1]);
        planePredictionMarker.setRotationAngle(angle);
      }
      planePredictionMarker.setLatLng(latlng);
    }
  }
}


////////////////////////////////////////////////////////////

/**
 * Displays distance from original point
 * @param {Object} e
 * @returns {undefined}
 */
function alertDistance(e) {
  if (rulerActive) {
    if (rulerStart === null) {
      rulerStart = { lat: e.latlng.lat, lon: e.latlng.lng };
    } else {
      const meters = geolib.getDistance(
        { latitude: rulerStart.lat, longitude: rulerStart.lon },
        { latitude: e.latlng.lat, longitude: e.latlng.lng },
        1, 1
      );
      alert.message(`${decround(mToFt(meters), 1)} ft`);
      rulerActive = false;
      rulerStart = null;
    }
  }
}

let _gimbal_marker = null;
function createGimbalMarker(e) {
  if (gimbalActive) {
    if (_gimbal_marker != null) removeObj(_gimbal_marker);
    _gimbal_marker = L.marker([e.latlng.lat, e.latlng.lng], { icon: gimbalIcon, zIndexOffset: 10 }).addTo(map);
    InteropActionCreator.gimbalLocation(e.latlng.lat, e.latlng.lng);
    gimbalActive = false;
  }
}

/**
 * Initializes basic features of the map (tile layer, controls, etc.)
 * @returns {undefined}
 */
function mapStarter() {
  L.tileLayer('img/plainWhiteSquare.png', {
    maxZoom: 19,
    minZoom: 16
  }).addTo(map);

  map.doubleClickZoom.disable();
  map.on('click', alertDistance);
  map.on('click', createGimbalMarker);
  map.on('click', () => {
    WaypointActionCreator.clearSelected();

  });
  map.on('dblclick', createTempMarker);

  L.easyButton({
    states: [
      {
        stateName: 'disable-zoom',
        icon: 'fa-compress',
        title: 'disable zoom',
        onClick: function (btn) {
          toggleZoom();
          btn.state('enable-zoom');
        }
      },
      {
        stateName: 'enable-zoom',
        icon: 'fa-expand',
        title: 'enable zoom',
        onClick: function (btn) {
          toggleZoom();
          btn.state('disable-zoom');
        }
      }
    ]
  }).addTo(map);


  L.easyButton({
    states: [
      {
        stateName: 'enable-track',
        icon: 'fa-plane',
        title: 'enable tracking',
        onClick: function (btn) {
          changeCenterOnPlane();
          btn.state('disable-track');
        }
      },
      {
        stateName: 'disable-track',
        icon: 'fa-map',
        title: 'disable tracking',
        onClick: function (btn) {
          changeCenterOnPlane();
          btn.state('enable-track');
        }
      }
    ]
  }).addTo(map);
  //Reset plane path button
  L.easyButton({
    states: [
      {
        stateName: 'reset-plane-path',
        icon: 'fa-times',
        title: 'reset plane path',
        onClick: resetPlanePath
      }
    ]
  }).addTo(map);
  L.easyButton({
    states: [
      {
        stateName: 'reset-splines',
        icon: 'fa-unlink',
        title: 'Reset splines',
        onClick: clearSplines
      }
    ]
  }).addTo(map);
  //start time ruler button
  L.easyButton({
    states: [
      {
        stateName: 'start-ruler',
        icon: 'fa-arrows-h',
        title: 'start ruler',
        onClick: function (btn) {
          startRuler();
          btn.state('end-ruler');
        }
      },
      {
        stateName: 'end-ruler',
        icon: 'fa-arrows-h',
        title: 'end ruler',
        onClick: function (btn) {
          startRuler();
          btn.state('start-ruler');
        }
      }
    ]
  }).addTo(map);
  //toggle showing target images
  L.easyButton({
    states: [
      {
        stateName: 'change-target-image',
        icon: 'fa-camera',
        title: 'change target image',
        onClick: function (btn) {
          changeTargetImgs();
          btn.state('change-target-image');
        }
      }
    ]
  }).addTo(map);
  //toggle pointing the gimbal
  L.easyButton({
    states: [
      {
        stateName: 'start-gimbal',
        icon: 'fa-crosshairs',
        title: 'start gimbal',
        onClick: function (btn) {
          startGimbal();
          btn.state('end-gimbal');
        }
      },
      {
        stateName: 'end-gimbal',
        icon: 'fa-crosshairs',
        title: 'end gimbal',
        onClick: function (btn) {
          startGimbal();
          btn.state('start-gimbal');
        }
      }
    ]
  }).addTo(map);
  //button to toggle coverage
  L.easyButton({
    states: [
      {
        stateName: 'show-coverage',
        icon: 'fa-square-o',
        title: 'show coverage',
        onClick: function (btn) {
          showCoverage();
          btn.state('hide-coverage');
        }
      },
      {
        stateName: 'hide-coverage',
        icon: 'fa-square-o',
        title: 'hide coverage',
        onClick: function (btn) {
          hideCoverage();
          btn.state('show-coverage');
        }
      }
    ]
  }).addTo(map);

  //button to clear coverage
  L.easyButton({
    states: [
      {
        stateName: 'clear-coverage',
        icon: 'fa-minus-square',
        title: 'Clear coverage',
        onClick: clearCoverage
      }
    ]
  }).addTo(map);

  //button to simulate coverage
  L.easyButton({
    states: [
      {
        stateName: 'simulate-coverage',
        icon: 'fa-puzzle-piece',
        title: 'Simulate coverage',
        onClick: simulateCoverage
      }
    ]
  }).addTo(map);

  //button for batch waypoint editing
  L.easyButton({
    states: [
      {
        stateName: 'batch-waypoint',
        icon: 'fa-cut',
        title: 'Batch waypoint editing',
        onClick: select_batch_waypoints()
      }
    ]
  }).addTo(map);

  //button to toggle being sda operator
  sdaSelectButton = L.easyButton('fa-code-fork', startSdaSelect).addTo(map);

  //button to remove sda wp
  L.easyButton('fa-eraser', deleteSda).addTo(map);
}

/**
 * Gets the index of a marker object in the array
 * @param {LeafletObject[]} array
 * @param {LeafletObject} object
 * @returns {number} index of object
 * @throws Object Not Found if no matching objects found
 */
function objectIndex(array, object) {
  const result = array.findIndex(element => Leaflet.stamp(element) === Leaflet.stamp(object));
  if (result === -1) throw 'Object Not Found';
  else return result;
}

/**
 * Confirm that the user wants to click on the waypoint
 * Only triggers warning if active and not recently clicked
 * @param {Event} e - drag event with target property
 * @returns {undefined}
 */
function confirmSelection(e) {
  const marker = e.target;
  const latlng = e.target.getLatLng();

  var object_list;
  var wp_list;
  const isSda = marker._popup._content[5] === 'S'; // check if contains "SDA", kinda hacky
  const isTemp = marker._popup._content[0] === 'T'; // check if contains "Temp", kinda hacky
  const sda_and_temp = isSda && isTemp;
  if (sda_and_temp) {
    object_list = _old_sda_waypoint_objects;
    wp_list = _old_sda_waypoints;
  } else if (isTemp) {
    object_list = _old_temp_waypoint_objects;
    wp_list = _old_temp_waypoints;
  } else {
    object_list = _old_waypoint_objects;
    wp_list = _old_waypoints;
  }

  const index = objectIndex(object_list, marker);
  const wp = wp_list[index];
  const wp_index = sda_and_temp ? index : wp.index;
  WaypointActionCreator.updateCellLatLon(wp_index, latlng.lat, latlng.lng, sda_and_temp);
  WaypointActionCreator.confirmSelectMap(wp_index, sda_and_temp);
}

/**
 * Sends the current active waypoint
 * @returns {undefined}
 */
function sendWP(quiet = false) {
  WaypointActionCreator.sendWaypoint(quiet);
}

function waypointDrag(e) {
  var marker = e.target;

  var object_list;
  var wp_list;
  const sda_and_temp = marker._popup._content[0] === 'T' && marker._popup._content[5] === 'S';
  if (sda_and_temp) {
    object_list = _old_sda_waypoint_objects;
    wp_list = _old_sda_waypoints;
  } else if (marker._popup._content[0] === 'T') {
    object_list = _old_temp_waypoint_objects;
    wp_list = _old_temp_waypoints;
  } else {
    object_list = _old_waypoint_objects;
    wp_list = _old_waypoints;
  }
  var index;
  try {
    index = objectIndex(object_list, marker);
  } catch (err) {
    // Marker no longer exists, drag was canceled.
    return;
  }

  var latlng = e.target.getLatLng();
  const wp = wp_list[index];
  const wp_index = sda_and_temp ? index : wp.index;
  WaypointActionCreator.updateCellLatLon(wp_index, latlng.lat, latlng.lng, sda_and_temp);
}

/**
 * Draws a waypoint to the waypointPath and adds a marker to the map
 * @param {Waypoint} waypoint
 * @returns {(LeafletObject|null)} drawn marker
 */
function draw_waypoint(waypoint, current_waypoint, selected_waypoint) {
  var wpMarkerIcon;
  var wpMarkerText;
  if (sdaSelectActive) {
    selected_waypoint = -1;
  }
  if (waypoint.type === 18) {
    return null;
  } else {
    if (waypoint.index === selected_waypoint && !waypoint.isTemp) {
      wpMarkerIcon = highlightMarkerIcon;
      wpMarkerText = `Selected Waypoint ${waypoint.index}`;
    } else if (waypoint.isTemp && waypoint.isSda) {
      wpMarkerIcon = tempMarkerIcon;
      wpMarkerText = 'Temp SDA Waypoint';
    } else if (waypoint.isTemp) {
      wpMarkerIcon = tempMarkerIcon;
      wpMarkerText = 'Temp Waypoint';
    } else if (waypoint.index === current_waypoint) {
      wpMarkerIcon = currentMarkerIcon;
      let dist = waypoint.min_dist == null ? 0 : decround(waypoint.min_dist, 0);
      wpMarkerText = `Waypoint ${waypoint.index}<br>MinDist: ${dist} m`;
    } else if (waypoint.isSda) {
      wpMarkerIcon = sdaMarkerIcon;
      let dist = waypoint.min_dist == null ? 0 : decround(waypoint.min_dist, 0);
      wpMarkerText = `SDA Waypoint ${waypoint.index}<br>MinDist: ${dist} m`;
    } else {
      wpMarkerIcon = getIcon(waypoint);
      let dist = waypoint.min_dist == null ? 0 : decround(waypoint.min_dist, 0);
      wpMarkerText = `Waypoint ${waypoint.index}<br>MinDist: ${dist} m`;
    }
    const popup = Leaflet.popup({ autoPan: false }).setContent(wpMarkerText);
    const marker = Leaflet.marker([waypoint.lat, waypoint.lon],
      { draggable: true, icon: wpMarkerIcon, zIndexOffset: 10 })
      .addTo(map).bindPopup(popup);
    marker.on('click', confirmSelection);
    marker.on('click', sdaSelect);
    marker.on('dragend', confirmSelection);
    marker.on('dragstart', () => { dragging = true; });
    marker.on('dragend', e => { dragging = false; waypointDrag(e); });
    if (waypoint.isTemp) {
      marker.on('drag', waypointDrag);
    } else {
      marker.on('dragend', () => { sendWP(true); });
    }
    return marker;
  }
}

/**
 * Selects the correct icon for a waypoint of a certain altitude
 * @param {Waypoint} waypoint 
 * @returns {Leaflet.icon} 
 */
function getIcon(waypoint) {
  const { alt } = waypoint;
  const max_height = 150.0;
  const index = Math.floor((_icons.length - 1) * alt / max_height) + 1;
  if (alt <= 5) return _icons[0];
  if (index > 5) return _icons[5];
  if (typeof _icons[index] === 'undefined') return _icons[0];
  else return _icons[index];
}

/**
 * Resets and draws a waypoint path (probably guards against GOTO values)
 * @param {Waypoint[]} waypoints - List of waypoints
 * @returns {undefined}
 */
function drawWaypointPath(waypoints) {
  waypointPath.setLatLngs([]);
  var i = 0;
  while (i < waypoints.length) {
    if (waypoints[i].type === 177 && !(Object.prototype.hasOwnProperty.call(waypoints[i], 'loops_left'))) {
      waypoints[i].loops_left = waypoints[i].lon;
    } else if (waypoints[i].type === 177 && typeof waypoints[i] === 'number' && waypoints[i].loops_left > 0) {
      waypoints[i].loops_left -= 1;
      i = waypoints[i].lat;
    } else if (waypoints[i].type === 177 && typeof waypoints[i] === 'number' && waypoints[i].loops_left <= 0) {
      delete waypoints[i].loops_left;
      i++;
    } else {
      if (Math.abs(waypoints[i].lat) > 1 && Math.abs(waypoints[i].lon) > 1) waypointPath.addLatLng([waypoints[i].lat, waypoints[i].lon]);
      i++;
    }
  }
}

function draw_sda_path(waypoints, sdaWaypoints, sdaStart, sdaEnd, sdaMode) {
  sdaPath.setLatLngs([]);
  if (!sdaMode) return;

  if (sdaStart !== -1 && sdaEnd != -1) {
    if (waypoints[sdaStart] != undefined) sdaPath.addLatLng([waypoints[sdaStart].lat, waypoints[sdaStart].lon]);
    if (sdaWaypoints.filter(wp => !wp.isSda).length == 0) waypoints.slice(sdaStart + 1, sdaEnd).map(wp => sdaPath.addLatLng([wp.lat, wp.lon]));
    sdaWaypoints.forEach(wp => sdaPath.addLatLng([wp.lat, wp.lon]));
    if (waypoints[sdaEnd] != undefined) sdaPath.addLatLng([waypoints[sdaEnd].lat, waypoints[sdaEnd].lon]);
  }
}

/**
 * Draws a geofence path
 * @param {Waypoint[]} waypoints
 * @returns {LeafletObject}
 */
function draw_geofence(waypoints) {
  let fullMap = [[[90, -180], [90, 180], [-90, 180], [-90, -180]]];
  const fence_points = waypoints.map(wp => [parseFloat(wp.lat), parseFloat(wp.lon)]);
  fullMap = fence_points.length > 0 ? fullMap.concat([waypoints]) : [];
  return L.polygon(fullMap, { color: 'red' }).addTo(map).bindPopup('Geofence');
}

function draw_coverage_boundary(coverage) {
  const boundary_points = coverage.map(pt => [parseFloat(pt.lat), parseFloat(pt.lon)]);
  return L.polygon(boundary_points, { color: 'blue', fill: false }).addTo(map).bindPopup('Search Boundary');
}

//Starts batch waypoint drag select
function select_batch_waypoints() {
  console.log("select");
}

/**
 * Draws an obstacle
 * @param {Obstacle} obstacle
 * @returns {LeafletObject}
 */
let firstCall = true;
let obstCount = 0;

function draw_obstacle(obstacle) {
  const stat = GlobalStore.getState();
  if (firstCall == true) {
    obstCount = obstCount + 1;
    if (obstCount === _old_obstacle_objects.stationary.length) {
      firstCall = false;
    }
    L.circle([obstacle.latitude, obstacle.longitude],
      obstacle.radius, { color: 'transparent', className: 'interactive-circle' }).addTo(map)
      .bindPopup('Cylinder, Height: ' + obstacle.height + ' m');
  }
  if (obstacle.radius == null) {
    return null;
  }
  else if (stat.status.gps.rel_alt <= obstacle.height) {
    return L.circle([obstacle.latitude, obstacle.longitude],
      obstacle.radius, { color: 'orange', className: 'interactive-circle' }).addTo(map)
      .bringToBack();
  }
  else if (stat.status.gps.rel_alt <= obstacle.height + 10) {
    return L.circle([obstacle.latitude, obstacle.longitude],
      obstacle.radius, { color: 'red', className: 'interactive-circle' }).addTo(map)
      .bringToBack();
  }
  else {
    return L.circle([obstacle.latitude, obstacle.longitude],
      obstacle.radius, { color: 'black', className: 'interactive-circle' }).addTo(map)
      .bringToBack();
  }
}

function draw_priority_region(color: string, point: Point) {
  return L.circle([point.lat, point.lon],
    ROI_RADIUS, { color: color, className: 'interactive-circle no-stroke' }).addTo(map);
}

function draw_roi(roi: Point) {
  return L.circle([roi.lat, roi.lon],
    ROI_RADIUS, { color: 'blue', className: 'interactive-circle no-stroke' }).addTo(map);
}
function draw_ADLC_target(target: Point) {
  return L.marker([target.lat, target.lon], { icon: adlc_icon, zIndexOffset: 20 }).addTo(map);
}

function draw_airdrop_location(location: Point) {
  return L.marker([location.lat, location.lon], { icon: airdrop_icon, zIndexOffset: 20 }).addTo(map);
}

function draw_splines(splines) {
  let prev_end = null;
  let result = [];
  for (let spline of splines) {
    if (prev_end === null || prev_end.lat !== spline.start.lat || prev_end.lon !== spline.start.lon) {
      result = result.concat(['M', [spline.start.lat, spline.start.lon]]);
    }
    result = result.concat(['C',
      [spline.control1.lat, spline.control1.lon],
      [spline.control2.lat, spline.control2.lon],
      [spline.end.lat, spline.end.lon]
    ]);
    prev_end = spline.end;
  }
  return L.curve(result, { color: 'purple' }).addTo(map);
}

var _old_yaw = 0;
var _old_gps = {};
/**
 * Updates the plane marker if the plane's heading or location has changed
 * @returns {undefined}
 */
function updatePlane(gps, attitude, connected, realistic) {
  if (!connected) {
    planeMarker.setIcon(planeIconHidden);
    return;
  } else if (realistic) {
    planeMarker.setIcon(planeIconRealistic);
  } else {
    planeMarker.setIcon(planeIcon);
  }
  if (attitude.yaw !== undefined && attitude.yaw !== _old_yaw) {
    let heading_normalized = ((attitude.yaw * 180 / Math.PI) + 360) % 360;
    planeMarker.setRotationAngle(heading_normalized);
    _old_yaw = attitude.yaw;
  }
  if (!_.isEqual(gps.lat, _old_gps.lat) || !_.isEqual(gps.lon, _old_gps.lon)) {
    planeMarker.setLatLng([gps.lat, gps.lon]);
    if (Math.abs(gps.lat) > 1 && Math.abs(gps.lon) > 1) planePath.addLatLng([gps.lat, gps.lon]);
  }
  if (_center_on_plane) centerOnPlane();
}

/**
 * Removes an object from the map (make sure to initialize map first)
 * @params {LeafletObject} layer - Must be a Leaflet ILayer
 * @returns {undefined}
 */
function removeObj(layer) {
  if (layer !== null) {
    map.removeLayer(layer);
  }
}

let _old_target_img = [];
let _old_target_img_objects = [];
function checkUpdateTargetImg(target_imgs) {
  if (target_imgs.length !== _old_target_img_objects.length) return false;
  let sameImg = true;
  for (let i = 0; i < target_imgs.length; i++) {
    sameImg = _.isEqual(target_imgs[i], _old_target_img[i]);
    if (!sameImg) return false;
  }
  return true;
}

function latLngToLeaflet(obj) {
  return L.latLng(obj.lat, obj.lon);
}

function updateTargetImg(target_imgs, distributedUrl) {
  if (targetImgOnMap && !checkUpdateTargetImg(target_imgs)) {
    _old_target_img_objects.forEach(removeObj);
    _old_target_img_objects = [];
    target_imgs.forEach(target_img => {
      const url = distributedUrl + target_img.imageUrl;
      const topLeft = latLngToLeaflet(target_img.topLeft);
      const topRight = latLngToLeaflet(target_img.topRight);
      const bottomLeft = latLngToLeaflet(target_img.bottomLeft);
      const overlay = L.imageOverlay.rotated(url, topLeft, topRight, bottomLeft).addTo(map);
      overlay.bringToFront();
      _old_target_img_objects.push(overlay);
    });
    _old_target_img = target_imgs;
  }
}

var _old_waypoints = [];
var _old_waypoint_objects = [];
var old_current = -1;
var old_selected = -1;
/**
 * Updates the waypoints if the waypoint list has changed
 * @returns {undefined}
 */
function updateWaypoints(waypoints, current_waypoint, selected_waypoint, force = false) {
  if (dragging && !force) {
    return;
  }
  var different = waypoints.length !== _old_waypoints.length;
  if (!different) {
    for (var i = 0; i < waypoints.length && !different; i++) {
      different = different ||
        waypoints[i].lat !== _old_waypoints[i].lat ||
        waypoints[i].lon !== _old_waypoints[i].lon ||
        waypoints[i].alt !== _old_waypoints[i].alt ||
        waypoints[i].type !== _old_waypoints[i].type;
    }
  }

  if (force || different || current_waypoint !== old_current || selected_waypoint !== old_selected) {
    _old_waypoint_objects.forEach(removeObj);
    _old_waypoint_objects = waypoints.map(wp => draw_waypoint(wp, current_waypoint, selected_waypoint));
    old_current = current_waypoint;
    old_selected = selected_waypoint;
  }
  _old_waypoints = _.cloneDeep(waypoints);
}

var _old_sda_waypoints = [];
var _old_sda_waypoint_objects = [];
function updateSdaWaypoints(waypoints, sdaWaypoints,
  current_waypoint, sdaStart, sdaEnd, sdaMode, selected_waypoint, force = false) {
  if (dragging) return;
  if (!sdaMode) sdaWaypoints = [];

  force = force == undefined ? false : force;
  var different = sdaWaypoints.length !== _old_sda_waypoints.length;
  if (!different) {
    for (var i = 0; i < sdaWaypoints.length && !different; i++) {
      different = different ||
        sdaWaypoints[i].lat !== _old_sda_waypoints[i].lat ||
        sdaWaypoints[i].lon !== _old_sda_waypoints[i].lon ||
        sdaWaypoints[i].alt !== _old_sda_waypoints[i].alt ||
        sdaWaypoints[i].min_dist !== _old_sda_waypoints[i].min_dist ||
        sdaWaypoints[i].type !== _old_sda_waypoints[i].type;
    }
  }

  if (force || different) {
    _old_sda_waypoint_objects.forEach(removeObj);
    _old_sda_waypoint_objects = sdaWaypoints.map(wp => draw_waypoint(wp, current_waypoint, null));
  }

  draw_sda_path(waypoints, sdaWaypoints, sdaStart, sdaEnd, sdaMode);
  _old_sda_waypoints = _.cloneDeep(sdaWaypoints);
}

var _old_temp_waypoints = [];
var _old_temp_waypoint_objects = [];
/**
 * Updates the temp waypoints if the temp waypoint list has changed
 * @returns {undefined}
 */
function updateTempWaypoints(temp_waypoints, current_waypoint, selected_waypoint) {
  if (dragging) {
    return;
  }
  var different = temp_waypoints.length !== _old_temp_waypoints.length;
  if (!different) {
    for (var i = 0; i < temp_waypoints.length && !different; i++) {
      different = different ||
        temp_waypoints[i].lat !== _old_temp_waypoints[i].original_lat ||
        temp_waypoints[i].lon !== _old_temp_waypoints[i].original_lon ||
        temp_waypoints[i].alt !== _old_temp_waypoints[i].original_alt ||
        temp_waypoints[i].type !== _old_temp_waypoints[i].original_type;
    }
  }

  if (different) {
    _old_temp_waypoint_objects.forEach(removeObj);
    _old_temp_waypoint_objects = temp_waypoints.map(wp => draw_waypoint(wp, current_waypoint, selected_waypoint));
  }
  _old_temp_waypoints = _.cloneDeep(temp_waypoints);
}

var _old_current = -1;
/**
 * Updates the current waypoint if it has changed
 * @returns {undefined}
 */
function updateCurrentWaypoint(current) {
  if (_old_waypoint_objects.length > 0) {
    if (_old_current >= 0 && _old_waypoint_objects[_old_current] != null && current !== _old_current) {
      _old_waypoint_objects[_old_current].setIcon(getIcon(_old_waypoints[_old_current]));
      if (_old_waypoint_objects[_old_current] != null) _old_waypoint_objects[_old_current].openPopup();
    }
    if (current < _old_waypoints.length && _old_waypoint_objects[current] != null && current !== _old_current) {
      _old_waypoint_objects[current].setIcon(currentMarkerIcon);
      if (_old_waypoint_objects[current] != null) _old_waypoint_objects[current].openPopup();
      _old_current = current;
    }
  }
}

var _old_splines = [];
var _old_spline_object = null;
function updateSplines(splines) {
  var different = splines.length !== _old_splines.length;
  if (!different) {
    for (var i = 0; i < splines.length && !different; i++) {
      different = different ||
        splines[i].lat !== _old_splines[i].lat ||
        splines[i].lon !== _old_splines[i].lon;
    }
  }

  if (different) {
    if (_old_spline_object !== null) removeObj(_old_spline_object);
    _old_spline_object = draw_splines(splines);
  }
  _old_splines = _.cloneDeep(splines);
}

var _old_geofence_objects = [];
/**
 * Updates the geofence
 * @returns {undefined}
 */
function updateGeofences(fence, enabled) {
  if (!enabled) {
    removeObj(_old_geofence_objects);
    _old_geofence_objects = null;
  } else {
    removeObj(_old_geofence_objects);
    _old_geofence_objects = draw_geofence(fence);
  }
}

let _old_coverage_boundary_object = null;
let _old_coverage_boundary = [];
/**
 * Updates the geofence
 * @returns {undefined}
 */
export function redrawCoverageBoundaries(coverage) {
  if (!_.isEqual(coverage, _old_coverage_boundary)) {
    removeObj(_old_coverage_boundary_object);
    _old_coverage_boundary_object = draw_coverage_boundary(coverage);
    _old_coverage_boundary = coverage;
  }
}

let _old_airdrop_location = { lat: 0, lon: 0 };
let _old_airdrop_object = null;
export function redrawAirdrop(location) {
  if (!_.isEqual(_old_airdrop_location, location)) {
    removeObj(_old_airdrop_object);
    _old_airdrop_object = draw_airdrop_location(location);
    _old_airdrop_location = location;
  }
}

let _old_obstacles = { stationary: [] };
let _old_obstacle_objects = { stationary: [] };
/**
 * Updates the obstacles
 * @returns {undefined}
 */
function updateObstacles(obstacles) {
  _old_obstacle_objects.stationary.forEach(removeObj);
  _old_obstacle_objects.stationary = obstacles.stationary.map(draw_obstacle);
  _old_obstacles.stationary = obstacles.stationary;

  // if (!_.isEqual(obstacles.moving, _old_obstacles.moving)) {
  //   _old_obstacle_objects.moving.forEach(removeObj);
  //   _old_obstacle_objects.moving = obstacles.moving.map(draw_obstacle);
  //   _old_obstacles.moving = obstacles.moving;
  // }
}

let _old_off_axis = { lat: 0, lon: 0 };
export function redrawOffAxis(off_axis, interopActive, interopAlive, gimbalLocation) {
  if (_gimbal_marker != null)
    _gimbal_marker.setLatLng([gimbalLocation.lat, gimbalLocation.lon]);

  if (!interopActive || !interopAlive) {
    offAxisMarker.setIcon(offAxisIconHidden);
    return;
  }
  if (off_axis !== _old_off_axis && off_axis !== undefined) {
    offAxisMarker.setIcon(offAxisIcon);
  }
  if (!_.isEqual(off_axis.lat, _old_off_axis.lat) || !_.isEqual(off_axis.lon, _old_off_axis.lon)) {
    offAxisMarker.setLatLng([off_axis.lat, off_axis.lon]);
  }
  _old_off_axis = off_axis;
}

let _old_priority_regions = { high: [], medium: [], low: [] };
let _old_priority_region_objects = { high: [], medium: [], low: [] };
function updatePriorityRegions(priority_regions: Object) {
  if (!_.isEqual(_old_priority_regions, priority_regions)) {
    _old_priority_region_objects.high.forEach(removeObj);
    _old_priority_region_objects.medium.forEach(removeObj);
    _old_priority_region_objects.low.forEach(removeObj);

    _old_priority_region_objects.high = priority_regions.high.map(region => draw_priority_region('green', region));
    _old_priority_region_objects.medium = priority_regions.medium.map(region => draw_priority_region('yellow', region));
    _old_priority_region_objects.low = priority_regions.low.map(region => draw_priority_region('red', region));

    _old_priority_regions = priority_regions;
  }
}

let _old_adlc_targets = [];
let _old_adlc_target_objects = [];
function updateADLCTargets(targets: Object[]) {
  if (!_.isEqual(_old_adlc_targets, targets) && Array.isArray(targets)) {
    _old_adlc_target_objects.forEach(removeObj);
    _old_adlc_target_objects = targets.map(draw_ADLC_target);
    _old_adlc_targets = targets;
  }
}

let _old_roi = [];
let _old_roi_objects = [];
function updateRoi(roi: Object[]) {
  if (!_.isEqual(_old_roi, roi) && Array.isArray(roi)) {
    _old_roi_objects.forEach(removeObj);
    _old_roi_objects = roi.map(draw_roi);
    _old_roi = roi;
  }
}

/**
 * Default location data, quickly overridden
 */
var locationsData = {
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
    'imageURL': 'img/satellites/SFO_Airport_Satellite.png',
    'bottomLat': -35.3688493943,
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
  'White Square': {
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
};

var locationMap2 = {
  'Neno Airfield': 'Neno_Airfield',
  'NAS Pax': 'NAS_Pax',
  'SFO Airport': 'SFO_Airport',
  'Cornell Campus': 'Cornell_Campus',
  'Game Farm': 'Game_Farm',
  'Earth Center': 'Earth_Center'
};

/**
 * Updates the locations data (image URL, coordinates, etc) and the location map
 * @params {object} locs
 * @returns {undefined}
 */
export function updateLocations(locs) {
  locationsData = locs;
  for (var name in locs) {
    locationMap2[name.replace(/_/g, ' ')] = name;
  }
}

/**
 * Changes the location of the map to the new location
 * @params {string} location - string of new map location
 * @returns {undefined}
 */
export function changeLocation(location) {

  current_location = location;
  location = locationMap2[location];
  if (location == undefined) location = 'Neno_Airfield';
  var loc = locationsData[location];

  const imageBounds = [[loc.bottomLat, loc.leftLon], [loc.topLat, loc.rightLon]];
  map.setMaxBounds(imageBounds);
  map.setView([(loc.topLat + loc.bottomLat) / 2, (loc.leftLon + loc.rightLon) / 2]);
  map.doubleClickZoom.disable();
  Leaflet.imageOverlay(loc.imageURL, imageBounds).addTo(map);
}

/**
 * Resets the plane's path (display only)
 * @returns {undefined}
 */
export function resetPlanePath() {
  planePath.setLatLngs([]);
}

/**
 * Redraws all waypoints
 * @returns {undefined}
 */
export function redrawWaypoints(waypoints, tempWaypoints,
  allWaypoints, sdaWaypoints, current, sdaStart,
  sdaEnd, sdaMode, selected_row, force = false) {
  updateWaypoints(waypoints, current, selected_row, force);
  updateTempWaypoints(tempWaypoints, current, selected_row);
  drawWaypointPath(allWaypoints);
  updateSdaWaypoints(waypoints, sdaWaypoints, current, sdaStart, sdaEnd, sdaMode, selected_row);
  updateCurrentWaypoint(current, selected_row);
}

export function redrawSplines(splines) {
  updateSplines(splines);
}

/**
 * Redraws Fences
 * @param {Point[]} fences
 * @param {boolean} enabled
 */
export function redrawFence(fences, enabled) {
  updateGeofences(fences, enabled);
}

/**
 * Redraws all obstacles
 * @param {ObstacleList} obstacles
 * @returns {undefined}
 */
export function redrawObstacles(obstacles) {
  updateObstacles(obstacles);
}


export function getCoverage() {
  if (coverage_img != null) {
    removeObj(coverage_img);
    coverage_img = null;
  }
  var loc = locationsData[locationMap2[current_location]] || locationsData[current_location];
  var imageBounds = [[loc.bottomLat, loc.leftLon], [loc.topLat, loc.rightLon]];
  var unixtime = new Date().getTime();
  // Add meaningless parameter to avoid caching issues
  coverage_img = L.imageOverlay('/static/img/coverage.png?t=' + unixtime.toString(), imageBounds);
  coverage_img.setOpacity(0.75);
  if (coverageActive) {
    coverage_img.addTo(map);
    coverage_img.bringToFront();
  }
}

/**
 * Redraws plane
 * @param {GPS} gps
 * @param {boolean} connected
 * @returns {undefined}
 */
export function redrawPlane(gps, attitude, connected, realistic) {
  updatePlane(gps, attitude, connected, realistic);
}

export function checkSda(sda) {
  if (!sda) sdaSelectButton.disable();
  else sdaSelectButton.enable();
}

export function redrawTargetImages(target_imgs, distributedUrl) {
  updateTargetImg(target_imgs, distributedUrl);
}

export function redrawPriorityRegions(priority_regions: Object, adlc_targets: Object[]) {
  updatePriorityRegions(priority_regions);
  updateADLCTargets(adlc_targets);
}

export function redrawRoi(roi) {
  updateRoi(roi);
}

/**
 * Causes map to redraw/resize
 * @returns {undefined}
 */
export function mapResize() {
  setTimeout(() => map.invalidateSize(), 100);
}

/**
 * Fully initializes the map
 * @returns {undefined}
 */
export function initializeMap() {
  setMap();
  setMarkers();
  setPaths();
  initializeMarkers();
  mapStarter();
}
