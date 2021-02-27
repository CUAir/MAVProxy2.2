// @flow

import $ from 'jquery';
import React from 'react';
import PropTypes from 'prop-types';

import { valueToColorName } from 'js/utils/ComponentUtils';
import { Dropdown, NavItem } from 'react-materialize';

function statusToClass(status) {
  return status ? 'green lighten-2' : 'red lighten-2';
}

type ItemType = {key: string, name: string, value: string};
function createInfo(item: ItemType) {
  return (
    <li key={item.name}>
      <span>
        <strong>{item.name}</strong>
        <div className='right' style={{paddingLeft: '20px'}}>{item.value}</div>
      </span>
    </li>
  );
}


class NavbarStatusItem extends React.Component {

  render() {
    const { name, id, status, dropdown = false, onClick = $.noop,
      half = false, items = [] } = this.props;
    
    const statusClass = statusToClass(status);
    const clickClass = onClick === $.noop ? 'no-back' : '';

    const clickable = (id) => {
      return <a id={id}>{name}</a>;
    }
    
    if (dropdown && items.length > 0) {
      const drop_id = `dropdown_${id.toLowerCase()}`;
      const color = status ? valueToColorName(100) : valueToColorName(0);
      const className = `${half ? 'status-bar-half ' : ''}${statusClass}`;
      return (
        <li className={className} id={id}>
          <Dropdown options={{constrainWidth: false, hover: true, belowOrigin: true}} 
            trigger={clickable(drop_id)}>
              {items.map(createInfo)}
          </Dropdown>
        </li>
      );
    } else {
      return (
        <li onClick={onClick} className={statusClass} id={id}>
          <a className={clickClass}>{name}</a>
        </li>
      );
    }
  }

}

NavbarStatusItem.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  status: PropTypes.bool.isRequired,
  dropdown: PropTypes.bool,
  onClick: PropTypes.func,
  half: PropTypes.bool,
  items: PropTypes.array
};

export default NavbarStatusItem;
