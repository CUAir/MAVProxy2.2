// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';
import { Input } from 'react-materialize'
import ConfirmationButton from 'js/components/General/ConfirmationButton';

type SettingsCheckboxType = {id?: string, name: string, value: boolean, confirm: boolean, onChange: Function};
function SettingsCheckbox({ id, name, value, onChange = $.noop, confirm = false}: SettingsCheckboxType) {
  const checkid = 'checkbox' + name.replace(/ /g, '');
  const ret_cb = !confirm || !value;

  const cb = (
    <div className='col s2' style={{ position: 'relative', marginTop: '1rem' }}>
      <p>
        <input 
          type='checkbox' 
          id={checkid} 
          checked={value}
          className='filled-in'
          onChange={ret_cb ? onChange : () => false}/>
        <label htmlFor={checkid}>{name}</label>
      </p> 
    </div>
  );

  if (ret_cb) 
    return cb;

  return (
    <ConfirmationButton
      key={id}
      name={`This action will result in permanent data loss`}
      onConfirm={onChange}
      onCancel={() => false}
      confirmation_text={`Are you sure you want to turn off ${name.split(" ")[0]}?`}>
      {cb}
    </ConfirmationButton>
  )
}

SettingsCheckbox.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  value: PropTypes.bool.isRequired
}

export default SettingsCheckbox;
