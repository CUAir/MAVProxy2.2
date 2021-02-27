// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

import { colorToButton } from 'js/utils/ComponentUtils';

type FullWidthFileInputType = {color: string, text: string, id?: string, onClick: Function};
function FullWidthFileInput({ color, text, id, onClick = $.noop }: FullWidthFileInputType) {
  const buttonClass = `btn full ${colorToButton(color)} btn-file`;
  return (
    <tr>
      <td colSpan='2'>
        <span className={buttonClass}>
          {text} <input type='file' id={id} onChange={onClick} />
        </span>
      </td>
    </tr>
  );
}

FullWidthFileInput.propTypes = {
  color: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  id: PropTypes.string,
  onClick: PropTypes.func
};

export default FullWidthFileInput;
