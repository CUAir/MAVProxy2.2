// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type SettingsFileInputType = {id?: string, name: string, onChange: Function};
function SettingsFileInput({ id, name, onChange = $.noop }: SettingsFileInputType) {
  return (
    <div className='col s4 file-field input-field'>
        <div className='btn'>
          <span>{name}</span>
          <input type='file' onChange={(e) => {onChange(e); e.target.value = ''}}/>
        </div>
        <div className='file-path-wrapper' style={{width: '0px', height: '0px'}}>
          <input className='file-path validate' type='text' style={{width: '0px', height: '0px'}} />
        </div>
    </div>
  );
}

SettingsFileInput.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string
};

export default SettingsFileInput;
