import { Record, List } from 'immutable';

import type { ObstacleType } from 'js/utils/Objects';
import type { InteropAction } from 'js/utils/Actions';


const Point = Record({
  lat: 0,
  lon: 0
});

const Cylinder = Record({
  latitude: 0,
  longitude: 0,
  radius: 0,
  height: 0
});

const InteropState = Record({
  alive: false,
  active: false,
  stationary: List(),
  off_axis: new Point(),
  mission_wp_dists: List(),
  gimbal: new Point(),
  offaxis_enabled: false,
  gimbal_status: false,
  waypoint_score: 0
});

const initialState = new InteropState();

type Obstacle = Cylinder;

function obstacleToImmutable(obstacle: ObstacleType): Obstacle {
  return new Cylinder(obstacle);
}

function scoreCalc(wpDists: number[]): number {
  return wpDists.reduce((a, b) => a + b, 0);
}

export default function InteropReducer(state: any = initialState, action: InteropAction) {
  switch (action.type) {
  case 'RECEIVE_INTEROP_ALIVE':
    return state
    .set('alive', action.alive);
  case 'RECEIVE_INTEROP_ACTIVE':
    return state
    .set('active', action.active);
  case 'RECEIVE_OBSTACLES':
    return state
    .set('stationary', List(action.obstacles.stationary_obstacles).map(obstacleToImmutable));
  case 'RECEIVE_OFF_AXIS':
    return state
    .set('off_axis', new Point(action.off_axis));
  case 'RECEIVE_MISSION_WP_DISTS':
    return state
    .set('mission_wp_dists', List(action.mission_wp_dists))
    .set('waypoint_score', scoreCalc(action.mission_wp_dists));
  case 'GIMBAL_LOCATION':
    return state
    .set('gimbal', new Point(action));
  case 'RECEIVE_OFFAXISTARGET_ENABLED':
    return state
    .set('offaxis_enabled', action.enabled);
  case 'GIMBAL_STATUS':
    return state
    .set('gimbal_status', action.status);
  default:
    return state;
  }
}
