// @flow

import React from 'react';
import PropTypes from 'prop-types';
import type { List } from 'immutable';
import ImmutablePropTypes from 'react-immutable-proptypes';
import { Input } from 'react-materialize'

import LocationButtonElement from 'js/components/Settings/LocationButtonElement';

type SettingsDropdownType = {value: string, options: List<Object>, name: string, id?: string, onSelect: Function};

function SettingsDropdown({ value = '', options, name, id, onSelect }: SettingsDropdownType) {
  return (
    <div className='col s4' style={{paddingLeft: '0px'}}>
     <Input
        type='select'
        label={name}
        defaultValue={value}
        onChange={(e) => onSelect(e.target.value)}
      >
      {options.map(item => (
        <option key={item.name}>
          {item.name}
        </option>
      ))}
      </Input>
    </div>
  );
}

SettingsDropdown.propTypes = {
  options: ImmutablePropTypes.list.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  id: PropTypes.string,
  onSelect: PropTypes.func
};

export default SettingsDropdown;
