'use strict';

import Highcharts from 'highcharts';
import geolib from 'geolib';
import _ from 'lodash';
import { List } from 'immutable';
import { PLANE_RECEIVE_FREQUENCY } from 'js/constants/Frequency';
import { decround } from 'js/utils/ComponentUtils';

// distance in meters to view ahead of and behind plane.
const x_window = 200;
// distance in meters to view above and below plane.
const y_window = 25;
// number of points to show behind plane.
const path_tail_length = 20;
// only draw this many waypoints (starting from current - 1)
const waypoints_to_draw = 5;

var chart;

function waypoint_to_series(waypoint, prev_x, x) {
  let series = List();

  let no_hover = {
    hover: {
      enabled: false
    }
  };
  let wp_marker = {
    symbol: 'url(img/altimeter/wp.png)',
    width: 15,
    height: 15
  };
  series = series.push({
    name: 'WP x',
    color: '#aa0000',
    data: [
      [prev_x, waypoint.alt],
      [x, waypoint.alt]
    ],
    states: no_hover
  });
  series = series.push({
    name: 'WP cross',
    data: [{
      x: x,
      y: waypoint.alt,
      marker: wp_marker
    }],
    states: no_hover
  });
  return series;
}

// computes distance in meter from wp_from to wp_to
function wp_dist(wp_from, wp_to) {
  return geolib.getDistance(
    {latitude: wp_from.lat, longitude: wp_from.lon},
    {latitude: wp_to.lat, longitude: wp_to.lon});
}

function get_xs(waypoints) {
  let xs = List([0]);
  _.range(1, waypoints.size).forEach((i) => {
    xs = xs.push(xs.get(i - 1) + wp_dist(waypoints.get(i - 1), (waypoints.get(i)))) ;
  });
  return xs;
}

function waypointsAreEqual(wps1, wps2, current_wp_i) {
  if (wps1 === wps2) return true;
  if (typeof wps2 == 'undefined' || wps1.size != wps2.size) {
    return false;
  }

  const start = Math.max(current_wp_i - 1, 1);
  const end = Math.min(start + waypoints_to_draw, wps1.size);
  for (let i = start; i < end; i++) {
    if (wps1.get(i).get('original_alt') != wps2.get(i).get('original_alt') ||
      wps1.get(i).get('original_lat') != wps2.get(i).get('original_lat') ||
      wps1.get(i).get('original_lon') != wps2.get(i).get('original_lon')) {

      return false;
    }
  }
  return true;
}

function makePlaneData(x, y) {
  const plane_marker = {
    symbol: 'url(img/altimeter/plane_side.png)',
    width: 25,
    height: 25
  };
  return [{
    x: x,
    y: y,
    selected: true,
    visible: true,
    marker: plane_marker
  }];
}

let waypoint_xs = List();
function redrawWaypointsHelper(waypoints, current_wp_i, mode, update_xs) {
  // Remove old waypoints
  waypoint_series_objects.forEach((wp_series) => wp_series.remove(false));
  waypoint_series_objects = [];

  if (last_mode == 'AUTO') {
    if (update_xs) waypoint_xs = get_xs(waypoints);
    
    // Construction the point and line for each waypoint
    const start = Math.max(current_wp_i - 1, 1);
    const end = Math.min(start + waypoints_to_draw, waypoints.size);
    for (let i = start; i < end; i++) {
      let waypoint_parts = waypoint_to_series(waypoints.get(i), waypoint_xs.get(i - 1), waypoint_xs.get(i));
      waypoint_parts.forEach((wp) => waypoint_series_objects.push(chart.addSeries(wp, false, false, false)));
    }
    chart.redraw(false);
  }
}


let old_waypoints = List();
let waypoint_series_objects = List();
let last_current = -1;

function redrawWaypoints(waypoints, current_wp_i, mode, mode_change, force) {
  if (!mode_change && !force && waypointsAreEqual(waypoints, old_waypoints, current_wp_i)) {
    if (last_current != current_wp_i) {
      redrawWaypointsHelper(waypoints, current_wp_i, mode, false); 
      last_current = current_wp_i; 
    }
    return;
  }
  last_current = current_wp_i;
  old_waypoints = waypoints;
  redrawWaypointsHelper(waypoints, current_wp_i, mode, true);
}

const latLonEps = 0.00001;
function gps_equal(gps, last_gps) {
  if (gps === last_gps) return true;
  return (Math.abs(last_gps.lat - gps.lat) < latLonEps &&
    Math.abs(last_gps.lon - gps.lon) < latLonEps);
}

let plane_x = 0;
let last_plane_x = 0;
let lat_alt = 0;
let last_gps = {
  rel_alt: null,
  lat: null,
  lon: null
};

function redrawPlane(gps, attitude, mode, waypoints, current_wp_index, mode_change, force) {
  if (!mode_change && !force && gps_equal(gps, last_gps)) return;
  if (current_wp_index >= waypoint_xs.size) return;

  if (mode_change) chart.get('plane_path_series').setData([], false, false, false);

  if (mode == 'AUTO') {
    // on landing just keep increase plane x
    if (current_wp_index != old_waypoints.size - 1) {
      plane_x = waypoint_xs.get(current_wp_index) - wp_dist(gps, waypoints.get(current_wp_index));
    } else {
      // we're on the landing waypoint. Just keep in increasing plane_x so 
      // we go through the waypoint instead of backwards.
      plane_x += gps.ground_speed * 1 / PLANE_RECEIVE_FREQUENCY;
    }
  } else {
    plane_x += gps.ground_speed * 1 / PLANE_RECEIVE_FREQUENCY;
  }

  if (plane_x < last_plane_x) {
    // clear the path if plane_x decreased because this causes weird things to happen
    chart.get('plane_path_series').setData([], false, false, false);
  }
  last_plane_x = plane_x;

  const shift = chart.get('plane_path_series').points.length > path_tail_length;
  chart.get('plane_path_series').addPoint([plane_x, decround(gps.rel_alt, 2)], false, shift, false);

  chart.get('plane_series').setData(makePlaneData(plane_x, decround(gps.rel_alt, 2)), false, false, false);
  chart.get('x_axis').setExtremes(plane_x - x_window, plane_x + x_window, false);

  // Only redraw y axis if we have really moved.
  if (Math.abs(lat_alt - gps.rel_alt) > 1) {
    chart.get('y_axis').setExtremes(Math.max(gps.rel_alt - y_window, -1), gps.rel_alt + y_window, false);
    lat_alt = gps.rel_alt;
  }

  chart.redraw();
  last_gps = gps;
}

let last_mode = '';
export function redraw(gps, attitude, mode, waypoints, current_wp_i, force = false) {
  const mode_change = last_mode != mode;
  last_mode = mode;
  redrawWaypoints(waypoints, current_wp_i, mode, mode_change, force);
  redrawPlane(gps, attitude, mode, waypoints, current_wp_i, mode_change, force);
}


export function initializeAltimeter(onClick) {
  const plane_path_style = {
    radius: 1,
    lineColor: '#666666',
    lineWidth: 1
  };

  const plane_marker = {
    symbol: 'url(img/altimeter/plane_side.png)',
    width: 25,
    height: 25
  };
  const plane_series = {
    id: 'plane_series',
    data: [{ x: 0, y: 0, selected: true, visible: true, marker: plane_marker}],
    dataLabels: { enabled: true }
  };
  const plane_path_series = {
    id: 'plane_path_series',
    data: [],
    dataLabels: { enabled: false},
    states: {hover: { enabled: false } }
  };

  const data = [plane_series, plane_path_series];

  chart = Highcharts.chart('altimeter_container', {

    chart: { type: 'spline', events: { click: onClick}},
    title: { text: '' },
    xAxis: { id: 'x_axis', visible: false },
    yAxis: { id: 'y_axis', title: { text: '' } },
    plotOptions: { spline: { marker: plane_path_style } },
    legend: { enabled: false },
    tooltip: { enabled: false },
    series: data
  });
}
