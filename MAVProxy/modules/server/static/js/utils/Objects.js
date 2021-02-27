// @flow

import type { OrderedMap } from 'immutable';

export type PointType = {
  lat: number,
  lon: number
};

type BatterySettingType = {
  cell2: number,
  cell6: number,
  cell9: number
};

export type FlightType = {
  avgDist: number,
  waypointScore: number,
  waypointCount: number,
  flightLength: number,
  flightStart: number,
  inFlight: string,
  manualTime: number,
  batteryBefore: BatterySettingType,
  batteryAfter: BatterySettingType,
  flights: Object[],
  windSpeed: string,
  windDirection: string,
  date: number,
  flightNotes: string,
  airframe: string
};

export type WaypointType = {
  isTemp: boolean,
  isSda: boolean,
  number: number,
  sda: boolean,
  type: number,
  alt: number,
  lat: number,
  lon: number,
  original_type: number,
  original_alt: number,
  original_lat: number,
  original_lon: number,
  index: number,
  edit_index: number,
  min_dist: number
};

export type MiniWaypointType = {
  altitude_msl: number,
  latitude: number,
  longitude: number
};

export type ParamType = {
  name: string,
  description: string,
  value: string,
  documentation: string,
  increment: number,
  key?: string,
  units: string,
  isTemp: boolean,
  values: OrderedMap<string, string>,
  originalValue: string,
  isTemp?: boolean
};

export type MiniParamType = {
  name: string,
  value: number,
  isTemp?: boolean
};

type CylinderType = {
  latitude: number,
  longitude: number,
  radius: number,
  height: number
};

export type ObstacleType = CylinderType;

export type PlanePathPointType = {
  time: number,
  lat: number,
  lon: number
};

export type PathSelectionType = {
  start: number,
  end: number
};

export type TargetImgType = {
  topLeft: PointType,
  topRight: PointType,
  bottomLeft: PointType,
  bottomRight: PointType,
  imageUrl: string
};

export type BatteryType = {
  batteryvoltage: number,
  batterypct: number
};

export type PowerboardType = {
  csbatt: number,
  nuc: number,
  gimbal: number,
  comms: number,
  '12v reg': number,
  '24v reg': number
};

export type AirspeedType = {
  airvx: number,
  airvy: number,
  airvz: number,
  speed: number,
  climb: number
};

export type AttitudeType = {
  pitch: number,
  roll: number,
  yaw: number,
  pitchspeed: number,
  rollspeed: number,
  yawspeed: number
};

export type GpsType = {
  lat: number,
  lon: number,
  rel_alt: number,
  ground_speed: number,
  groundvx: number,
  groundvy: number,
  groundvz: number,
  heading: number
};

export type WindType = {
  windvx: number,
  windvy: number,
  windvz: number,
  wind_speed: number
};

export type LinkType = {
  packet_loss: number,
  num: number,
  device: string,
  num_lost: number,
  link_delay: number,
  device_name: string,
  alive: boolean
};

export type PriorityRegionObject = {
  high: PointType[],
  medium: PointType[],
  low: PointType[]
};
