// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type FullWidthTextInputType = {name: string, id?: string, onChange: Function, value: string};
function FullWidthTextInput({ name, id, onChange = $.noop, value = '' }: FullWidthTextInputType) {
  return (
    <tr>
      <td><p className='middle-center'>{name}</p></td>
      <td>
        <div className='input-group full'>
          <input
            type='text'
            id={id}
            className='form-control'
            onChange={onChange}
            value={value}
          />
        </div>
      </td>
    </tr>
  );
}

FullWidthTextInput.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  onChange: PropTypes.func,
  value: PropTypes.string
};

export default FullWidthTextInput;
