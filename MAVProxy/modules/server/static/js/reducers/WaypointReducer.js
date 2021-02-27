import { Record, List } from 'immutable';
import $ from 'jquery';

import { valueClose, alert } from 'js/utils/ComponentUtils';
import * as SendApi from 'js/utils/SendApi';
import { redrawWaypoints } from 'js/utils/MapUtils';

const zero_checks = Object.freeze([16, 17, 20, 22]);
const DEFAULT_WP_HEIGHT = 150;
// const { List } = require('immutable');

const Waypoint = Record({
  isTemp: false, isSda: false, number: -1, sda: false, type: -1,
  alt: 0, lat: 0, lon: 0, original_type: -1, original_alt: 0, original_lat: 0,
  original_lon: 0, index: 0, min_dist: 0, edit_index: 0
});

const Point = Record({
  lat: 0, lon: 0
});

const Spline = Record({
  start: new Point(),
  control1: new Point(),
  control2: new Point(),
  end: new Point()
});

function scroll_to_current(current_waypoint) { // eslint-disable-line no-unused-vars
  // scroll the waypoint list to the new current waypoint using jquery animations
  const scroll_offset = $(`#wp-${current_waypoint}`).offset().top
    - $('.waypointContainer').offset().top + $('.waypointContainer').scrollTop()
    - $('.waypointContainer').height() * 1 / 5;
  $('.waypointContainer').animate({ scrollTop: scroll_offset }, 300);
}

function get_index(waypoints, index) {
  if (index <= 0) return 1;
  else if (!waypoints.get(index).isTemp) return waypoints.get(index).number + 1;
  else return get_index(waypoints, index - 1);
}

function reorder_waypoints(waypoints, to, frm) {
  const wp_to = to < waypoints.size ? to : waypoints.size - 1;
  waypoints = waypoints.splice(frm, 1).splice(wp_to, 0, waypoints.get(frm).set('index', to));
  return waypoints.map((wp, i) => wp.set('index', i));
}

function interpolate_Altitude(waypoints, sda_waypoints, sda_start, sda_end, sda, lat, lon) {
  var altNum = DEFAULT_WP_HEIGHT;
  if (sda) {
    var lat_1 = Math.pow((waypoints.get(sda_start).lat - lat), 2);
    var lon_1 = Math.pow((waypoints.get(sda_start).lon - lon), 2);
    var lat_2 = Math.pow((waypoints.get(sda_end).lat - lat), 2);
    var lon_2 = Math.pow((waypoints.get(sda_end).lon - lon), 2);
    var x1 = Math.sqrt(lat_1 + lon_1);
    var x2 = Math.sqrt(lat_2 + lon_2);
    var z_start = waypoints.get(sda_start).alt;
    var z_end = waypoints.get(sda_end).alt;
    altNum = Math.abs(((z_start * x2) + (z_end * x1)) / (x2 + x1));
  }
  return altNum;
}

function add_temp_waypoint(waypoints, sda_waypoints, sda, lat, lon, sda_start, sda_end) {
  const latNum = typeof lat !== 'number' ? 0 : lat;
  const lonNum = typeof lon !== 'number' ? 0 : lon;
  const altNum = interpolate_Altitude(waypoints, sda_waypoints, sda_start, sda_end, sda, latNum, lonNum);
  const waypoint = new Waypoint({
    isTemp: true, isSda: sda, lat: latNum, lon: lonNum, type: 16, alt: altNum, original_type: 16, original_alt: 0,
    original_lat: latNum, original_lon: lonNum, index: waypoints.size, edit_index: waypoints.size
  });
  const relevant_wps = sda ? sda_waypoints : waypoints;
  return relevant_wps.push(waypoint);
}

function make_wp_from_server_wp(wp, index, sdaMeansTemp) {
  const temp = sdaMeansTemp ? wp.sda : false;
  if (wp.isTemp) {
    return new Waypoint(wp);
  } else {
    return new Waypoint({
      isTemp: temp, isSda: wp.sda, number: index, type: wp.command,
      alt: wp.alt, lon: wp.lon, lat: wp.lat, original_type: wp.command,
      original_alt: wp.alt, original_lon: wp.lon, original_lat: wp.lat,
      min_dist: wp.min_dist, index: index, edit_index: index
    });
  }
}

function waypoint_equality(wp1, wp2) {
  return wp1.isSda === wp2.isSda &&
    wp1.isTemp === wp2.isTemp &&
    wp1.number === wp2.number &&
    valueClose(wp1.original_alt, wp2.original_alt) &&
    wp1.original_lat === wp2.original_lat &&
    wp1.original_lon === wp2.original_lon &&
    wp1.min_dist === wp2.min_dist &&
    wp1.original_type === wp2.original_type;
}

function receive_waypoints_sda(old_waypoints, new_waypoints_server) {
  let new_waypoints = List(new_waypoints_server.map((waypoint, i) => make_wp_from_server_wp(waypoint, i, true)));

  // Check to see if the waypoints have actually changed
  const waypoints_have_not_changed = new_waypoints.size === old_waypoints.size && new_waypoints.every((new_wp, index) =>
    old_waypoints.get(index) != undefined && waypoint_equality(old_waypoints.get(index), new_wp)
  );

  return waypoints_have_not_changed ? old_waypoints : new_waypoints;
}


// Check if a ground station waypoint is the same as a sever waypoint.
function wp_same(server_wp, server_index, gcs_wp) {
  if (typeof gcs_wp == 'undefined') {
    return false;
  }
  return valueClose(server_wp.alt, gcs_wp.original_alt) &&
    server_index == gcs_wp.number &&
    server_wp.lat == gcs_wp.original_lat &&
    server_wp.lon == gcs_wp.original_lon &&
    (server_wp.min_dist > 99 ||
      server_wp.min_dist == gcs_wp.min_dist) &&
    server_wp.command == gcs_wp.original_type;
}

// Check if a ground station temp waypoint is the same as a sever waypoint.
function wp_same_temp(server_wp, gcs_wp) {
  if (typeof gcs_wp == 'undefined') {
    return false;
  }
  return valueClose(server_wp.alt, gcs_wp.alt) &&
    server_wp.lat == gcs_wp.lat &&
    server_wp.lon == gcs_wp.lon &&
    server_wp.command == gcs_wp.type;
}

// Check if there's a difference between the gcs_waypoints and the 
// server waypoints. Return the new waypoints if there is or gcs_waypoints 
// if there was no change. 
function receive_waypoints(gcs_waypoints, server_waypoints) {
  let waypoints_have_changed = false;
  let new_waypoints = List();
  let gcs_wp_index = 0;

  // Construct the new waypoint list. To do so, copy all temp waypoints and 
  // use server waypoints if they are different than GCS waypoints. We may 
  // find nothing has changed and then return the old waypoints, gcs_waypoints.
  server_waypoints.forEach((server_wp, server_index) => {
    // get gcs_wp or undefined.
    let gcs_wp = gcs_waypoints.get(gcs_wp_index);

    let matched_temp = false;
    // push all temp waypoints into new waypoint list.
    while (typeof gcs_wp != 'undefined' && gcs_wp.isTemp && !matched_temp) {
      if (wp_same_temp(server_wp, gcs_wp)) {
        // The GCS has successful received this temp waypoint. Replace it with
        // a real one.
        waypoints_have_changed = true;
        matched_temp = true;
        new_waypoints = new_waypoints.push(make_wp_from_server_wp(server_wp, gcs_wp_index));
      } else {
        new_waypoints = new_waypoints.push(gcs_wp);
        gcs_wp = gcs_waypoints.get(++gcs_wp_index);
      }
    }
    // If we matched a temp, we've already handled this server waypoint.
    if (!matched_temp) {
      // push old waypoint if it seems to be the same.
      if (wp_same(server_wp, server_index, gcs_wp)) {
        new_waypoints = new_waypoints.push(gcs_wp);
      } else {
        waypoints_have_changed = true;
        new_waypoints = new_waypoints.push(make_wp_from_server_wp(server_wp, server_index));
      }
    }

    gcs_wp_index++;
  });

  // Copy any extra temp wps that are at the end of the gcs waypoint list
  for (; gcs_wp_index < gcs_waypoints.size; gcs_wp_index++) {
    const gcs_wp = gcs_waypoints.get(gcs_wp_index);
    if (gcs_wp.isTemp) {
      new_waypoints = new_waypoints.push(gcs_wp);
    }
  }

  // If the waypoints have changed use the new waypoints. Also, if the gcs_list
  // is too long, return the new list.
  if (waypoints_have_changed || gcs_waypoints.size != new_waypoints.size) {
    return new_waypoints;
  }
  return gcs_waypoints;
}

function receive_competition_waypoints(waypoints, gcs_waypoints) {
  let mission_waypoints = [];
  let waypoint_index = 0;
  let gcs_waypoint_0 = gcs_waypoints.get(0);
  // let com0 = gcs_waypoint_0.type;
  let altNum0 = gcs_waypoint_0.alt;
  let latNum0 = gcs_waypoint_0.lat;
  let lonNum0 = gcs_waypoint_0.lon;
  mission_waypoints.push({
    // 'command':com0,
    'lon': lonNum0,
    'lat': latNum0,
    'alt': altNum0
  });

  for (; waypoint_index < waypoints.length; waypoint_index += 1) {
    let waypoint = waypoints[waypoint_index];
    let altNum = waypoint['altitude'];
    let latNum = waypoint['latitude'];
    let lonNum = waypoint['longitude'];
    mission_waypoints.push({
      'command': 16,
      'lon': lonNum,
      'lat': latNum,
      'alt': altNum
    });
  }

  if (gcs_waypoints.size > 1) {
    for (let i = 1; i < gcs_waypoints.size; i++) {
      let gcs_waypoint = gcs_waypoints.get(i);
      // let com = gcs_waypoint.type;
      let altNum = gcs_waypoint.alt;
      let latNum = gcs_waypoint.lat;
      let lonNum = gcs_waypoint.lon;
      mission_waypoints.push({
        // 'command': com,
        'lon': lonNum,
        'lat': latNum,
        'alt': altNum
      });
    }
  }
  return mission_waypoints;
}

function receive_sda_endpoints(start, end, buf) {
  let points = [start, end];
  SendApi.sendPointsForPathPlanning(points, buf);
}

function delete_sda_endpoint() {
  SendApi.deleteSdaWps();
}

function validate_waypoint(wp) {
  if (isNaN(Number(wp.alt)) || wp.alt < 0) {
    alert.warning('Waypoint altitude must be greater than zero');
    return false;
  } else if (isNaN(Number(wp.lat)) || wp.lat < -90 || wp.lat > 90) {
    alert.warning('Waypoint latitude out of range');
    return false;
  } else if (isNaN(Number(wp.lon)) || wp.lon < -180 || wp.lat > 180) {
    alert.warning('Waypoint longitude out of range');
    return false;
  } else {
    return true;
  }
}

function load_waypoints(waypoints) {
  if (waypoints.some(wp => !validate_waypoint(wp))) return;
  const send_waypoints = waypoints.map(wp => Object.assign({}, wp, { item: wp.command }));
  SendApi.sendWaypointList(send_waypoints);
}

function set_current(waypoints, selected_row) {
  if (selected_row == -1) alert.warning('No waypoint selected!');
  else if (waypoints.get(selected_row).isTemp) alert.warning('Can\'t set temp waypoint to current!');
  else SendApi.setCurrentWP(selected_row);
}

function get_bounded_wps(waypoints, area) {
  const wps = waypoints.shift();
  const selected = wps.filter(wp => area.getBounds().contains({ lat: wp.lat, lng: wp.lon }));
  const l = selected.map(wp => wp.index);
  return selected;
}

function confirm_select(index, isSda, onYes, onNo, waypoint_list, last_change, selected_sda, selected_row) {
  const d = (new Date()).getTime();
  if (isSda) {
    selected_sda = index;
    if (onYes != null) onYes();
  } else if (waypoint_list.get(index).isTemp) {
    selected_row = index;
    if (onYes != null) onYes();
  } else if (d - last_change < 10000 || confirm('Are you sure you want to edit an on-board waypoint?')) {
    last_change = d;
    selected_row = index;
    if (onYes != null) onYes();
  } else {
    if (onNo != null) onNo();
  }
  return {
    last_change, selected_sda, selected_row
  };
}

function confirm_select_map(index, isSda, waypoint_list, sda_waypoints, last_change,
  selected_sda, selected_row, current_waypoint, sda_start, sda_end, sda_mode) {
  const d = (new Date()).getTime();
  let output_waypoints;
  if (isSda) {
    selected_sda = index;
    output_waypoints = waypoint_list;
  } else if (waypoint_list.getIn([index, 'isTemp'])) {
    selected_row = index;
    output_waypoints = waypoint_list;
  } else if (d - last_change < 10000 || confirm('Are you sure you want to edit an on-board waypoint?')) {
    last_change = d;
    selected_row = index;
    output_waypoints = waypoint_list;
  } else {
    // cancel drag
    let wp = waypoint_list.get(index);

    output_waypoints = waypoint_list.setIn([index, 'lat'], wp.original_lat).setIn([index, 'lon'], wp.original_lon);

    redrawWaypoints(
      output_waypoints.filter(wp => !wp.isTemp).toJS(),
      output_waypoints.filter(wp => wp.isTemp).toJS(),
      sda_waypoints.toJS(),
      current_waypoint,
      sda_start,
      sda_end,
      sda_mode,
      true
    );
  }
  return {
    selected_sda, selected_row, last_change, output_waypoints
  };
}

function send_helper(waypoint, selected_row, waypoints) {
  if (waypoint.isTemp) {
    const index = selected_row == 0 ? 0 : get_index(waypoints, selected_row);
    SendApi.sendWaypoint(waypoint.toJS(), index);
    return waypoints;
  } else {
    const index = selected_row;
    const previousTempWaypointCount = waypoints.slice(0, index).filter(wp => wp.isTemp).size;
    SendApi.updateWP(waypoint.toJS(), index - previousTempWaypointCount);
    return waypoints;
  }
}

function send_waypoint(selected_row, waypoints, quiet = false) {
  if (selected_row == -1) {
    if (!quiet) alert.warning('No waypoint selected!');
    return waypoints;
  }

  const waypoint = waypoints.get(selected_row);
  if ((!waypoint.isTemp &&
    waypoint.type == waypoint.original_type &&
    waypoint.lat == waypoint.original_lat &&
    waypoint.lon == waypoint.original_lon &&
    waypoint.alt == waypoint.original_alt)
    || !validate_waypoint(waypoint)) {
    return waypoints;
  }

  if (zero_checks.indexOf(waypoint.type) !== -1 && waypoint.alt === 0) {
    const isConfirm = confirm('This waypoint has altitude 0, are you sure you want to send it?');
    if (isConfirm) {
      return send_helper(waypoint, selected_row, waypoints);
    } else {
      alert.warning('Waypoint was not sent');
      return waypoints;
    }
  } else {
    return send_helper(waypoint, selected_row, waypoints);
  }
}

// function delete_waypoint(selected_row, selected_sda, waypoints, sda_waypoints, sda_from_server) {
//   if (selected_row == -1 && selected_sda != -1) {
//     sda_waypoints = sda_waypoints.splice(selected_sda, 1);
//     if (sda_waypoints.length === 0) sda_from_server = false;
//   } else {
//     const waypoint = waypoints.get(selected_row);
//     if (waypoint.isTemp) waypoints = waypoints.splice(selected_row, 1);
//     else SendApi.deleteWP(waypoint.number);
//     selected_row = -1;
//   }

//   return { selected_row, waypoints, sda_waypoints, sda_from_server };
// }


// function delete_waypoint(selected_row, selected_sda, waypoints, sda_waypoints, sda_from_server, selected_wps) {
//   if (selected_wps.size == 0 && selected_sda != -1) {
//     console.log("sda")
//     sda_waypoints = sda_waypoints.splice(selected_sda, 1);
//     if (sda_waypoints.length === 0) sda_from_server = false;
//   } else {
//     // const waypoint = waypoints.get(selected_row);
//     const selected_wps_index = selected_wps.map(wp => wp.index);
//     console.log("way", waypoints)
//     // console.log("sel", selected_wps)
//     console.log("row", selected_row)
//     // waypoints = waypoints.map(wp => selected_wps.contains(wp) && wp.isTemp
//     //   ? waypoints.splice(wp.index, 1)
//     //   : SendApi.deleteWP(wp.number));
//     if (selected_row != -1) {
//       console.log("heree")
//       var row_wp = waypoints.get(selected_row);
//       if (row_wp.isTemp) {
//         console.log("here")
//         waypoints = waypoints.splice(row_wp.index, 1);
//       } else {
//         SendApi.deleteWP(row_wp.number);
//       }
//     } else if (selected_wps.size > 0) {
//       for (var wp_idx = selected_wps_index.size - 1; wp_idx >= 0; wp_idx--) {
//         var wp = waypoints.get(selected_wps_index.get(wp_idx));
//         if (wp.isTemp) {
//           waypoints = waypoints.splice(wp.index, 1);
//         }
//         else {
//           SendApi.deleteWP(wp.number);
//         }
//       }
//     }

//     waypoints = waypoints.map((wp, idx) => wp.set('index', idx));

//     // if (waypoint.isTemp) waypoints = waypoints.splice(selected_row, 1);
//     // else SendApi.deleteWP(waypoint.number);
//     selected_row = -1;
//   }

//   console.log("wps", waypoints)
//   return { selected_row, waypoints, sda_waypoints, sda_from_server, selected_wps };
// }

const timer = ms => new Promise(res => setTimeout(res, ms))
function delete_waypoint(selected_row, selected_sda, waypoints, sda_waypoints, sda_from_server, selected_wps) {
  if (selected_wps.size == 0 && selected_sda != -1) {
    sda_waypoints = sda_waypoints.splice(selected_sda, 1);
    if (sda_waypoints.length === 0) sda_from_server = false;
  } else {
    const selected_wps_index = selected_wps.map(wp => wp.index);
    console.log("rowNum", selected_row);
    if (selected_row != -1) {
      var row_wp = waypoints.get(selected_row);
      if (row_wp.isTemp) {
        waypoints = waypoints.splice(row_wp.index, 1);
      } else {
        SendApi.deleteWP(row_wp.number);
      }
    } else if (selected_wps.size > 0) {
      console.log("wps", waypoints)
      console.log("sel", selected_wps)
      for (var wp_idx = selected_wps_index.size - 1; wp_idx >= 0; wp_idx--) {
        var wp = waypoints.get(selected_wps_index.get(wp_idx));
        console.log("sel wp", selected_wps, wp_idx)
        console.log("idx, number", wp.index, wp.number)
        if (wp.isTemp) {
          waypoints = waypoints.splice(wp.index, 1);
        }
        else {
          console.log("number", wp.number)
          SendApi.deleteWP(wp.number);
          // await timer(500);
          waypoints = waypoints.splice(wp.index, 1);
        }
      }
    }
    // waypoints = waypoints.map((wp, idx) =>
    //   wp.set('index', idx).set('edit_index', idx)
    // );

    selected_row = -1;
  }
  waypoints = waypoints.map((wp, i) => wp.set('index', i));
  console.log("ret", waypoints)
  // reorder_waypoints(waypoints, 0, waypoints.length - 1)
  // console.log("ret", waypoints)
  return { selected_row, waypoints, sda_waypoints, sda_from_server, selected_wps };
}

function send_all_helper(waypoints) {
  SendApi.sendAllWaypoints(waypoints);
  return waypoints.filter(wp => !wp.isTemp);
}

function send_all_waypoints(waypoints) {
  if (waypoints.find(wp => zero_checks.indexOf(wp.type) !== -1 && wp.alt === 0) != undefined) {
    const isConfirm = confirm('One of your waypoints has altitude 0, are you sure you want to send them?');
    if (isConfirm) {
      return send_all_helper(waypoints);
    } else {
      alert.warning('Waypoints were not sent');
      return waypoints;
    }
  } else {
    return send_all_helper(waypoints);
  }
}

function send_all_sda_helper(waypoints, sda_start, sda_end, sda_waypoints) {
  const before = waypoints.slice(0, sda_start + 1);
  const after = waypoints.slice(sda_end);
  const all = before.concat(sda_waypoints).concat(after);
  SendApi.sendAllSdaWaypoints(all.toJS());
  return {
    sda_start: -1, sda_end: -1, sda_waypoints: List(), sda_from_server: false
  };
}

function send_all_sda_waypoints(waypoints, sda_waypoints, sda_start, sda_end, sda_from_server) {
  if (sda_waypoints.size === 0) {
    alert.warning('No SDA Waypoints to send');
  } else if ((sda_start >= 0) && (sda_end > (sda_start + 1)) && sda_waypoints.filter(wp => !wp.isTemp).size == 0) {
    alert.warning('Manual-only sda paths must consist of a single path');
  } else if ((sda_start < 0 || sda_end < 0) && (waypoints.filter(wp => !wp.isTemp).size > 0)) {
    alert.warning('Please select an SDA path before sending');
  } else if (!sda_from_server) {
    if (sda_waypoints.find(wp => zero_checks.indexOf(wp.type) !== -1 && wp.alt === 0) != undefined) {
      const isConfirm = confirm('One of your waypoints has altitude 0, are you sure you want to send them?');
      if (isConfirm) {
        ({ sda_start, sda_end, sda_waypoints, sda_from_server } = send_all_sda_helper(waypoints, sda_start, sda_end, sda_waypoints));
      } else {
        alert.warning('Waypoints were not sent');
      }
    } else {
      ({ sda_start, sda_end, sda_waypoints, sda_from_server } = send_all_sda_helper(waypoints, sda_start, sda_end, sda_waypoints));
    }
  } else if (sda_start >= 0 && sda_end >= 1) {
    if (sda_waypoints.find(wp => zero_checks.indexOf(wp.type) !== -1 && wp.alt === 0) != undefined) {
      const isConfirm = confirm('One of your waypoints has altitude 0, are you sure you want to send them?');
      if (isConfirm) {
        ({ sda_start, sda_end, sda_waypoints, sda_from_server } = send_all_sda_helper(waypoints, sda_start, sda_end, sda_waypoints));
      } else {
        alert.warning('Waypoints were not sent');
      }
    } else {
      ({ sda_start, sda_end, sda_waypoints, sda_from_server } = send_all_sda_helper(waypoints, sda_start, sda_end, sda_waypoints));
    }
  } else if (waypoints.size <= 1) {
    SendApi.sendAllSdaWaypoints(sda_waypoints.toJS());
    sda_waypoints = List();
  } else {
    alert.warning('No start and end points selected');
  }

  return { sda_waypoints, sda_start, sda_end, sda_from_server };
}

function insert_coverage_waypoints(original_waypoints, new_waypoints, current_waypoint) {
  new_waypoints.forEach(waypoint => {
    waypoint.isTemp = true;
    waypoint.type = 16;
    waypoint.original_type = waypoint.type;
    waypoint.original_alt = waypoint.alt;
    waypoint.original_lat = waypoint.lat;
    waypoint.original_lon = waypoint.lon;
  });

  const new_waypoints_immutable = List(new_waypoints.map(Waypoint));
  return original_waypoints.splice(current_waypoint + 1, 0, ...new_waypoints_immutable);
}

function update_selected_alt(wps, selected_wps, index, key, newValue) {
  const selected_wps_index = selected_wps.map(wp => wp.index);
  if (selected_wps_index.includes(index) && key == "alt") {
    wps = wps.map(wp => selected_wps_index.includes(wp.index) ? wp.set("alt", newValue) : wp)
  }
  return wps;
}

function update_selected_latlon(wps, selected_wps, index, lat, lon) {
  const selected_wps_index = selected_wps.map(wp => wp.index);
  if (selected_wps_index.includes(index)) {
    const transLat = lat - wps.get(index).lat
    const transLon = lon - wps.get(index).lon
    wps = wps.map(wp => selected_wps_index.includes(wp.index)
      ? wp.set("lat", wp.lat + transLat).set("lon", wp.lon + transLon)
      : wp)
  }
  // .set(waypoint_name, wplist.setIn([index, 'lat'], lat).setIn([index, 'lon'], lon));
  wps.forEach(wp => {
    if (!wp.isTemp) {
      send_waypoint(wp.index, wps)
    }
  })
  return wps;
}

const WaypointState = Record({
  selected_row: -1,
  selected_sda: -1,
  selected_wps: List(),
  waypoints: List(),
  sda_waypoints: List(),
  waypoints_completed: 0,
  is_tracking: false,
  current_waypoint: 0,
  show_all_sda: false,
  sda_start: -1,
  sda_end: -1,
  sda_from_server: false,
  last_change: 0,
  splines: List(),
  sdaMode: localStorage['sdaMode'] === 'true'
});
// sdaMode is being tracked in settingsReducer too, not ideal but
// should be fine, maybe look into how reducers can access each others'
// state at some point (may create weird data dependencies?)

const initialState = new WaypointState();

export default function waypointReducer(state: any = initialState, action) {
  switch (action.type) {
    case 'RECEIVE_SDA_MODE':
      return state
        .set('sdaMode', action.sdaMode);
    case 'REORDER_WAYPOINTS':
      return state
        .set('selected_row', -1)
        .set('selected_sda', -1)
        .set('waypoints', reorder_waypoints(state.waypoints, action.start, action.end));
    case 'REORDER_WAYPOINTS_SDA':
      return state
        .set('selected_row', -1)
        .set('selected_sda', -1)
        .set('sda_waypoints', reorder_waypoints(state.sda_waypoints, action.start, action.end));
    case 'WAYPOINT_UPDATE_CELL': {
      const { sda, index, key, newValue } = action;
      console.log(index)
      const waypoint_name = sda ? 'sda_waypoints' : 'waypoints';
      const wplist = state.get(waypoint_name);
      const new_wps = state.selected_wps.size > 0
        ? update_selected_alt(wplist, state.selected_wps, index, key, newValue)
        : wplist.setIn([index, key], newValue);
      console.log("new", new_wps)
      return state
        .set(waypoint_name, new_wps)
    }
    case 'WAYPOINT_UPDATE_CELL_LAT_LON': {
      const { sda, index, lat, lon } = action;
      const waypoint_name = sda ? 'sda_waypoints' : 'waypoints';
      const wplist = state.get(waypoint_name);
      const new_wps = state.selected_wps.size > 0
        ? update_selected_latlon(wplist, state.selected_wps, index, lat, lon)
        : wplist.setIn([index, 'lat'], lat).setIn([index, 'lon'], lon);
      return state
        .set(waypoint_name, new_wps);
    }
    case 'WAYPOINT_INC_SELECTED':
      if (action.is_sda) {
        let new_sel = state.selected_sda + 1;
        if (new_sel >= state.sda_waypoints.size) new_sel = state.sda_waypoints.size - 1;
        return state
          .set('selected_row', -1)
          .set('selected_sda', new_sel);
      } else {
        let new_sel = state.selected_row + 1;
        if (new_sel >= state.waypoints.size) new_sel = state.waypoints.size - 1;
        return state
          .set('selected_row', new_sel)
          .set('selected_sda', -1);
      }
    case 'WAYPOINT_DEC_SELECTED':
      if (action.is_sda) {
        let new_sel = state.selected_sda == -1 ? state.sda_waypoints.size - 1 : state.selected_sda - 1;
        if (new_sel < 0) new_sel = 0;
        return state
          .set('selected_row', -1)
          .set('selected_sda', new_sel);
      } else {
        let new_sel = state.selected_row == -1 ? state.waypoints.size - 1 : state.selected_row - 1;
        if (new_sel < 0) new_sel = 0;
        return state
          .set('selected_row', new_sel)
          .set('selected_sda', -1);
      }
    case 'WAYPOINT_SET_SELECTED':
      return state
        .set('selected_row', action.number)
        .set('selected_sda', -1);
    case 'WAYPOINT_LIST_SET_SELECTED':
      return state
        .set('selected_wps', get_bounded_wps(state.waypoints, action.area));
    case 'WAYPOINT_LIST_CLEAR_SELECTED':
      return state
        .set('selected_wps', List())
        .set('selected_row', -1);
    case 'WAYPOINT_SET_SELECTED_SDA':
      return state
        .set('selected_row', -1)
        .set('selected_sda', action.number);
    case 'WAYPOINT_ADD': {
      const { lat, lon } = action;
      const waypoint_name = state.sdaMode ? 'sda_waypoints' : 'waypoints';
      return state
        .set(waypoint_name, add_temp_waypoint(state.get('waypoints'), state.get('sda_waypoints'), state.sdaMode, lat, lon, state.sda_start, state.sda_end));
    }
    case 'SAVE_FLIGHT':
      return state
        .set('waypoints_completed', 0);
    case 'CHANGE_TRACKING':
      // if (action.tracking) scroll_to_current(state.get('current_waypoint'));
      return state
        .set('is_tracking', action.tracking);
    case 'WAYPOINTS_RECEIVE_CURRENT': {
      // if (state.get('current_waypoint') !== action.current) scroll_to_current(action.current);
      const changedCurrent = state.current !== action.current_waypoint ? 1 : 0;
      return state
        .set('waypoints_completed', state.waypoints_completed + changedCurrent)
        .set('current_waypoint', action.current);
    }
    case 'CHANGE_SHOW_SDA':
      return state
        .set('show_all_sda', action.show);
    case 'WAYPOINTS_RECEIVE_PATH':
      receive_sda_endpoints(action.selection.start, action.selection.end, action.selection.buf);
      return state
        .set('sda_start', action.selection.start)
        .set('sda_end', action.selection.end);
    case 'WAYPOINTS_RECEIVE':
      return state
        .set('waypoints', receive_waypoints(state.waypoints, action.waypoints));
    case 'WAYPOINTS_RECEIVE_SDA':
      return state
        .set('sda_from_server', true)
        .set('sda_waypoints', receive_waypoints_sda(state.sda_waypoints, action.waypoints));
    case 'WAYPOINTS_LOAD_FROM_FILE':
      load_waypoints(action.wps);
      return state
        .set('waypoints', List());
    case 'COMPETITION_WAYPOINTS_RECEIVE':
      load_waypoints(receive_competition_waypoints(action.waypoints, state.waypoints));
      return state
        .set('waypoints', List());
    case 'WAYPOINT_DELETE_ALL_SDA':
      delete_sda_endpoint();
      return state
        .set('sda_waypoints', List())
        .set('sda_start', -1)
        .set('sda_end', -1)
        .set('sda_from_server', false);
    case 'WAYPOINT_SET_CURRENT':
      set_current(state.waypoints, state.selected_row);
      return state;
    case 'WAYPOINT_CONFIRM_SELECT': {
      const { last_change, selected_sda, selected_row } = confirm_select(
        action.index, action.sda, action.onYes, action.onNo, state.waypoints,
        state.last_change, state.selected_sda, state.selected_row
      );
      return state
        .set('last_change', last_change)
        .set('selected_sda', selected_sda)
        .set('selected_row', selected_row);
    }
    case 'WAYPOINT_CONFIRM_SELECT_MAP': {
      const { selected_sda, selected_row, last_change, output_waypoints } = confirm_select_map(
        action.index, action.sda, state.waypoints, state.sda_waypoints,
        state.last_change, state.selected_sda, state.selected_row,
        state.current_waypoint, state.sda_start, state.sda_end, state.sdaMode
      );
      return state
        .set('selected_sda', selected_sda)
        .set('selected_row', selected_row)
        .set('last_change', last_change)
        .set('waypoints', output_waypoints);
    }
    case 'WAYPOINT_SEND_ALL':
      return state
        .set('waypoints', send_all_waypoints(state.waypoints));
    case 'WAYPOINT_SEND_ALL_SDA': {
      const { sda_waypoints, sda_start, sda_end, sda_from_server } = send_all_sda_waypoints(
        state.waypoints, state.sda_waypoints, state.sda_start, state.sda_end, state.sda_from_server
      );
      return state
        .set('sda_waypoints', sda_waypoints)
        .set('sda_start', sda_start)
        .set('sda_end', sda_end)
        .set('sda_from_server', sda_from_server);
    }
    case 'WAYPOINT_SEND':
      return state
        .set('waypoints', send_waypoint(state.selected_row, state.waypoints, action.quiet));
    case 'WAYPOINT_DELETE': {
      const { selected_row, waypoints, sda_waypoints, sda_from_server } = delete_waypoint(
        state.selected_row, state.selected_sda, state.waypoints, state.sda_waypoints, state.sda_from_server, state.selected_wps
      );
      return state
        .set('selected_row', selected_row)
        .set('waypoints', waypoints)
        .set('sda_waypoints', sda_waypoints)
        .set('sda_from_server', sda_from_server)
        .set('selected_wps', List());
    }

    case 'RECEIVE_SPLINES':
      return state.set('splines', List(action.splines.map(Spline)));
    case 'RECEIVE_COVERAGE_POINTS':
      return state.set('waypoints', insert_coverage_waypoints(state.waypoints, action.points, state.current_waypoint));
    case 'CLEAR_TEMP_WPS':
      return state.set('waypoints', state.waypoints.filter(wp => !wp.isTemp));
    default:
      return state;
  }
}
