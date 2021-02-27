import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';

import GlobalStore from 'js/stores/GlobalStore';

import { getLocations } from 'js/utils/ReceiveApi';
import { redrawWaypoints, redrawFence, redrawObstacles, redrawPlane,
         redrawOffAxis, initializeMap, changeLocation, updateLocations,
         redrawTargetImages, checkSda, redrawSplines, redrawPriorityRegions, redrawRoi, redrawCoverageBoundaries, 
         getCoverage, drawPlanePredictionPath, updatePlanePredictionMarker, redrawAirdrop } from 'js/utils/MapUtils';

const style = {width: '100%', height: '690px'};

function mapStateToProps({ settings: { slider_visible } }) {
  return {
    slider_visible
  };
}

function linterpolate(frm, to, rel_from, rel_to, rel_current) {
  let res = frm + (rel_current - rel_from) * ((to - frm) / (rel_to - rel_from));
  return res;
}

class MapSection extends React.Component {
  
  animation_interval = null;
  animation = null;

  constructor(props) {
    super(props);
    this.animation_interval = setInterval(() => false, 1000);
    this.animation = {
      start: {},
      current: {},
      target: {},
      frame: 0,
      frames: 1000,
      last_update: Math.floor(Date.now()),
      frame_incr: 50 
    };
    clearInterval(this.animation_interval);
  }

  componentDidMount() {
    initializeMap();
    this._updateAll();
    getLocations();

    GlobalStore.subscribe(this._fenceChange);
    GlobalStore.subscribe(this._interopChange);
    GlobalStore.subscribe(this._sdaChange);
    GlobalStore.subscribe(this._statusChange);
    GlobalStore.subscribe(this._settingsChange);
    GlobalStore.subscribe(this._targetImgChange);
    GlobalStore.subscribe(this._coverageChange);
    GlobalStore.subscribe(this._wpChange);
  }

  existing_waypoints = null;

  updateTrackingPoint(gps, attitude, connected) {
    let now = Math.floor(Date.now());
    if (now - this.animation.last_update < 100) return;
    clearInterval(this.animation_interval);
  
    this.animation.last_update = now;

    this.animation.frame = this.animation.frame_incr;
    if(this.animation.current.gps === undefined) {
      // first frame so lag behind for a second
      this.animation.start.gps = {};
      this.animation.current.gps = {};
      this.animation.target.gps = {};
      this.animation.start.gps.lat = gps.lat;
      this.animation.current.gps.lat = gps.lat;
      this.animation.target.gps.lat = gps.lat;
      this.animation.start.gps.lon = gps.lon;
      this.animation.current.gps.lon = gps.lon;
      this.animation.target.gps.lon = gps.lon;
      this.animation.start.attitude = {};
      this.animation.current.attitude = {};
      this.animation.target.attitude = {};
      this.animation.start.attitude.yaw = attitude.yaw;
      this.animation.current.attitude.yaw = attitude.yaw;
      this.animation.target.attitude.yaw = attitude.yaw;
    } else {
      this.animation.start.gps.lat = this.animation.current.gps.lat;
      this.animation.start.gps.lon = this.animation.current.gps.lon;
      this.animation.target.gps = gps;
      this.animation.start.attitude.yaw = this.animation.current.attitude.yaw;
      this.animation.target.attitude = attitude;
    }

    this.animation_interval = setInterval(() => {
      this.animation.current.gps.lat = linterpolate(
        this.animation.start.gps.lat,
        this.animation.target.gps.lat,
        0, this.animation.frames, this.animation.frame);
      this.animation.current.gps.lon = linterpolate(
        this.animation.start.gps.lon,
        this.animation.target.gps.lon,
        0, this.animation.frames, this.animation.frame);
      let yaw_s = this.animation.start.attitude.yaw;
      let yaw_t = this.animation.target.attitude.yaw;
      // the following code accounts for weird rollover in yaw
      if (yaw_s * yaw_t < 0 && Math.max(yaw_s, yaw_t) - Math.min(yaw_s, yaw_t) > 1) { // rollover from -pi to pi
        if (yaw_s < yaw_t) yaw_s += 2 * Math.PI
        else yaw_t += 2 * Math.PI
      } else if(Math.max(yaw_s, yaw_t) - Math.min(yaw_s, yaw_t) > 4) { // rollover from 2pi to 0
        if (yaw_s > yaw_t) yaw_s -= 2 * Math.PI
        else yaw_t -= 2 * Math.PI
      }
      this.animation.current.attitude.yaw = linterpolate( yaw_s, yaw_t,
        0, this.animation.frames, this.animation.frame);

      redrawPlane(this.animation.current.gps, this.animation.current.attitude, connected, true);
      if (this.animation.frame < this.animation.frames)
        this.animation.frame = Math.floor(Date.now()) - this.animation.last_update;
    }, this.animation.frame_incr);
  }

  @autobind
  _wpChange() {
    const { waypoints, settings } = GlobalStore.getState();
    if (waypoints === this.existing_waypoints && settings === this.existing_settings) return;
    this.existing_waypoints = waypoints;
    this.existing_settings = settings;

    const wps = waypoints.waypoints.toJS();
    redrawWaypoints(wps.filter(wp => !wp.isTemp), wps.filter(wp => wp.isTemp), wps,
      waypoints.sda_waypoints.toJS(), waypoints.current_waypoint,
      waypoints.sda_start, waypoints.sda_end, settings.sdaMode, waypoints.selected_row);
    const { splines } = waypoints;
    redrawSplines(splines.toJS());
  }

  existing_fences = null;

  @autobind
  _fenceChange() {
    const { fences } = GlobalStore.getState();
    if (fences === this.existing_fences) return;
    this.existing_fences = fences;

    redrawFence(fences.points.toJS(), fences.enabled);
  }

  existing_interop = null;

  @autobind
  _interopChange() {
    const { interop } = GlobalStore.getState();
    if (interop === this.existing_interop) return;
    this.existing_interop = interop;

    redrawOffAxis(interop.off_axis.toJS(), interop.active, interop.alive, interop.gimbal);
    redrawObstacles({stationary: interop.stationary.toJS()});
  }

  existing_sda = null;

  @autobind
  _sdaChange() {
    const { sda } = GlobalStore.getState();
    if (sda === this.existing_sda) return;
    this.existing_sda = sda;

    if (sda.plane_path.size !== 0) {
      drawPlanePredictionPath(sda.plane_path.toJS());
      updatePlanePredictionMarker(time_at_reset, 0);
    }

  }

  existing_status = null;

  @autobind
  _statusChange() {
    const { status, settings: { smooth_animation } } = GlobalStore.getState();
    if (status === this.existing_status) return;
    this.existing_status = status;
    if (smooth_animation) {
      this.updateTrackingPoint(status.gps.toJS(), status.attitude.toJS(), status.connected)
    } else {
      clearInterval(this.animation_interval);
      redrawPlane(status.gps.toJS(), status.attitude.toJS(), status.connected, false);
    }
  }

  existing_settings = null;

  @autobind
  _settingsChange() {
    const { settings } = GlobalStore.getState();
    if (settings === this.existing_settings) return;
    this.existing_settings = settings;

    updateLocations(settings.location_data.toJS());
    changeLocation(settings.location);
    checkSda(settings.sdaMode);
  }

  existing_target_img = null;

  @autobind
  _targetImgChange() {
    const { targetImage, settings } = GlobalStore.getState();
    if (targetImage === this.existing_target_img && settings === this.existing_settings) {
      return;
    }
    this.existing_target_img = targetImage;
    this.existing_settings = settings;

    redrawTargetImages(targetImage.target_images.toJS(), settings.distributedUrl);
    redrawCoverageBoundaries(targetImage.coverage.toJS());
    redrawPriorityRegions(targetImage.priority_regions.toJS(), targetImage.adlc_targets.toJS());
    redrawRoi(targetImage.roi);
    redrawAirdrop(targetImage.airdrop_location.toJS());
  }

  cur_cov_version = -1;

  @autobind
  _coverageChange(){
    const { targetImage } = GlobalStore.getState();

    if (targetImage.coverage_version != this.cur_cov_version) {
      this.cur_cov_version = targetImage.coverage_version;
      getCoverage();
    }
  }

  @autobind
  _updateAll() {
    this._wpChange();
    this._fenceChange();
    this._interopChange();
    this._sdaChange();
    this._statusChange();
    this._settingsChange();
    this._targetImgChange();
    this._coverageChange();
  }

  render() {
    const sectionclass = this.props.slider_visible ? 'map-with-slider' : 'full-height';
    return (
      <div id='mapSection' className={sectionclass}>
        <div id='map' style={{width: '100%', background: 'fafafa'}} className='full-height'></div>
      </div>
    );
  }
}


export default connect(mapStateToProps)(MapSection);
