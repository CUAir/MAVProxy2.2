import React from 'react';

import { sendWaypoint, confirmSelect, cellChange } from 'js/actions/WaypointActionCreator';
import { mToFt, ftToM, decround } from 'js/utils/ComponentUtils';
import { Dropdown, NavItem } from 'react-materialize';
import { Input } from 'react-materialize'

const wp_types = Object.freeze({
  16: { name: 'WAYPOINT', icon: 'map-marker' },
  17: { name: 'LOITER', icon: 'paper-plane' },
  177: { name: 'DO JUMP', icon: 'undo' },
  20: { name: 'RTL', icon: 'home' },
  21: { name: 'LAND', icon: 'angle-double-down' },
  22: { name: 'TAKEOFF', icon: 'angle-double-up' }
});

function handleChange(event, index, baseAltitude, keyName, units, sda, isTemp) {
  const baseAlt = index === 0 ? 0 : baseAltitude;
  const value = keyName === 'alt' && !units && event.target.value !== '' ? (ftToM(event.target.value) - baseAlt) : event.target.value;
  cellChange(index, keyName, value, sda && isTemp);
}

function handleKeyGen(n) {
  return (e) => {
    if (e.key === 'Enter') {
      $(`#msave-${n}`).click();
    }
  }
}

function WaypointCell({ id, name, value, index, wp, units, sda_temp, min, max }) {

  const onChangeGen = (key) => {
    return (e) => {
      let updated_val = e.target.value;
      if (key === 'num')
        return cellChange(index, 'edit_index', parseInt(updated_val), sda_temp);
      if (key === 'alt' && !units)
        updated_val = ftToM(updated_val);
      if (key === 'type')
        updated_val = parseInt(updated_val);
      if (typeof updated_val === 'string')
        updated_val = parseFloat(updated_val);
      cellChange(index, key, updated_val, sda_temp);
    }
  }

  var inp_class = wp[id] === wp['original_' + id] ? 'black-text' : 'red-text';
  if (id === 'num')
    inp_class = wp['index'] === wp['edit_index'] ? 'black-text' : 'red-text';

  if (id === 'type') {
    return (
      <div className='col s2' key={id + '-' + index}>
        <Input
          type='select'
          label={name}
          className={inp_class}
          value={'' + value}
          onChange={onChangeGen('type')} >
          {Object.keys(wp_types).map(k =>
            <option key={wp_types[k].name} value={k}>{wp_types[k].name}</option>
          )}
        </Input>
      </div>
    );
  }

  return (
    <div className='input-field col s2 validate' key={id + '-' + index}>
      <input
        value={value}
        id={'' + id + index}
        type='number'
        className={inp_class + ' validate'}
        onChange={onChangeGen(id)}
        onKeyDown={handleKeyGen(index)}
        step={id === 'lat' || id === 'lon' ? 0.0001 : 1}
        min={min}
        max={max} />
      <label className='active' htmlFor={'' + id + index}>{name}</label>
    </div>
  );
}

export default WaypointCell;
