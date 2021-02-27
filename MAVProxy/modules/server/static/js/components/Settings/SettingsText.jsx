// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type SettingsTextType = {id?: string, name: string, value: string, onChange: Function};
function SettingsText({ id, name, value, onChange = $.noop }: SettingsTextType) {
  let formid = 'textid' + name.replace(/ /g, '');
  return (
    <div className='input-field col s4'>
      <input
        id={formid}
        type='text'
        defaultValue={value}
        onChange={onChange} />
      <label htmlFor={formid} className='active'>{name}</label>
    </div>
  );
}

SettingsText.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string.isRequired,
    PropTypes.number.isRequired
  ])
}

export default SettingsText;
