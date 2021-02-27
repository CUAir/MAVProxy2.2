// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';
import ConfirmationButton from 'js/components/General/ConfirmationButton';

type SettingsCriticalButtonType = {id?: string, name: string, onClick: Function};
function SettingsCriticalButton({ id, name, onClick = $.noop }: SettingsCriticalButtonType) {
  return (
    <div className='col s4 input-field'>         
      <ConfirmationButton
        name={`Are you sure you want to ${name.toLowerCase()} the plane?`}
        onConfirm={onClick}
        onCancel={() => false}
        confirmation_text='This action must be done when on the ground, if the vehicle is in the air, this action will result in a crash.'>
        <button className='btn red'>
              {name}
        </button>
      </ConfirmationButton>
    </div>
  );
}

SettingsCriticalButton.propTypes = {
  onClick: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string
};

export default SettingsCriticalButton;
