// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type SettingsButtonType = {onClick: Function, name: string, id?: string};
function SettingsButton({ onClick = $.noop, name, id }: SettingsButtonType) {
  return (
    <div className='col s4 input-field'>
        <button onClick={onClick} className='btn'>
          {name}
        </button>
    </div>
  );
}

SettingsButton.propTypes = {
  onClick: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string
};

export default SettingsButton;
