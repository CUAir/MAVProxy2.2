// @flow

import React from 'react';
import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';

import { BatteryValuePropType } from 'js/utils/PropTypes';
import { valueToPercent, valueToColor, decround, colorToButton } from 'js/utils/ComponentUtils';

type BatteryType = {value: {batteryvoltage: number, batterypct: number}};
function Battery({ value: { batteryvoltage, batterypct } }: BatteryType) {
  const percent = Math.min(decround(batterypct, 2), 100);
  const voltage = decround(batteryvoltage, 2);
  const className = valueToColor(percent);
  const innerstyle = {minWidth: '120px', height: '100%'};  
  return (
    <li key='BATTERY' id='BATTERY' className={className}>
      <a style={innerstyle}>
        {percent}%, {voltage}V
      </a>
    </li>
  );
}

Battery.propTypes = {
  value: BatteryValuePropType.isRequired
}

export default Battery;
