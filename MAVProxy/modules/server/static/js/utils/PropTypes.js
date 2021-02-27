// @flow

import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';

export const BatteryPropType = ImmutablePropTypes.recordOf({
  cell2: PropTypes.number.isRequired,
  cell6: PropTypes.number.isRequired,
  cell9: PropTypes.number.isRequired
});

export const BatteryValuePropType = ImmutablePropTypes.recordOf({
  batteryvoltage: PropTypes.number.isRequired,
  batterypct: PropTypes.number.isRequired
});

export const GpsPropType = ImmutablePropTypes.recordOf({
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  rel_alt: PropTypes.number.isRequired,
  ground_speed: PropTypes.number.isRequired,
  groundvx: PropTypes.number.isRequired,
  groundvy: PropTypes.number.isRequired,
  groundvz: PropTypes.number.isRequired,
  heading: PropTypes.number.isRequired
});

export const AirspeedPropType = ImmutablePropTypes.recordOf({
  airvx: PropTypes.number.isRequired,
  airvy: PropTypes.number.isRequired,
  airvz: PropTypes.number.isRequired,
  speed: PropTypes.number.isRequired,
  climb: PropTypes.number.isRequired
});

export const AttitudePropType = ImmutablePropTypes.recordOf({
  pitch: PropTypes.number.isRequired,
  roll: PropTypes.number.isRequired,
  yaw: PropTypes.number.isRequired,
  pitchspeed: PropTypes.number.isRequired,
  rollspeed: PropTypes.number.isRequired,
  yawspeed: PropTypes.number.isRequired
});

export const WindPropType = ImmutablePropTypes.recordOf({
  windvx: PropTypes.number.isRequired,
  windvy: PropTypes.number.isRequired,
  windvz: PropTypes.number.isRequired,
  wind_speed: PropTypes.number.isRequired
});

export const PointPropType = ImmutablePropTypes.recordOf({
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired
});
