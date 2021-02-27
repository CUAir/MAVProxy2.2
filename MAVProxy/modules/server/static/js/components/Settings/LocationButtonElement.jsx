// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type LocationButtonElementType = {onClick: Function, name: string};
function LocationButtonElement({ onClick = $.noop, name }: LocationButtonElementType) {
  return <li onClick={onClick}><a>{name}</a></li>;
}

LocationButtonElement.propTypes = {
  onClick: PropTypes.func,
  name: PropTypes.string.isRequired
}

export default LocationButtonElement;
