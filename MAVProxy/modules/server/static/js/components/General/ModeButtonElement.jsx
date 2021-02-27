// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type ModeButtonElementType = {name: string, onClick: Function};
function ModeButtonElement({ name, onClick = $.noop }: ModeButtonElementType) {
  return <li onClick={onClick}><a>{name}</a></li>;
}

ModeButtonElement.propTypes = {
  onClick: PropTypes.func,
  name: PropTypes.string.isRequired
};

export default ModeButtonElement;
