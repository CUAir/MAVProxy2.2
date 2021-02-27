// @flow

import React from 'react';
import PropTypes from 'prop-types';

import { m_sToKnots, decround, mToFt } from 'js/utils/ComponentUtils';

const speeds = Object.freeze(['Ground Speed', 'Air Speed', 'Wind Speed', 'Climb Rate']);

type PlaneInfoItemType = {id?: string, name: string, value: string | number,
  unit: string, unitSwitch: boolean};
function PlaneInfoItem({ id, name, value, unit, unitSwitch = true }: PlaneInfoItemType) {
  let v, u;
  if (!unitSwitch) {
    if (speeds.indexOf(name) >= 0) {
      v = decround(m_sToKnots(value), 2);
      u = 'knots';
    } else if (name === 'Rel. Alt.') {
      v = decround(mToFt(parseFloat(value)), 2);
      u = 'ft';
    } else {
      v = value;
      u = unit;
    }
  } else {
    v = value;
    u = unit;
  }

  return (
    <li id={id} className='collection-item' style={{paddingTop: '6px', paddingBottom: '6px'}}>
      <div>
        {name}
        <a className='right grey-text text-darken-2'>{v} {u}</a>
      </div>
    </li>
  );
}

PlaneInfoItem.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  unit: PropTypes.string.isRequired,
  unitSwitch: PropTypes.bool
};

export default PlaneInfoItem;
