// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

import { colorToButton } from 'js/utils/ComponentUtils';

type FullWidthButtonType = {color: string, onClick: Function, id?: string, text: string, style?: Object};
function FullWidthButton({ color, onClick = $.noop, id, text, style }: FullWidthButtonType) {
  return (
    <button className={`btn ${color}`} onClick={onClick} style={{width: '100%', margin: '5px'}} key={id} >
      {text}
    </button>
  );
}

FullWidthButton.propTypes = {
  color: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  id: PropTypes.string,
  text: PropTypes.string.isRequired,
  style: PropTypes.object
};

export default FullWidthButton;
