// @flow

import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';

type NavbarLinkItemType = {onClick: Function, name: string};
function NavbarLinkItem({ onClick = $.noop, name }: NavbarLinkItemType) {
  return (
    <li>
      <a onClick={onClick}>{name}</a>
    </li>
  );
}

NavbarLinkItem.propTypes = {
  onClick: PropTypes.func,
  name: PropTypes.string.isRequired
};

export default NavbarLinkItem;
