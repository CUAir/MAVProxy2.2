// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import $ from 'jquery';
import PropTypes from 'prop-types';

import ModeButtonElement from 'js/components/General/ModeButtonElement';
import { Dropdown, NavItem } from 'react-materialize';

/**
 * @module components/PlaneAction/ModeButton
 */

function getModeButtonElement(name: string, item: Object) {
  const onClick = typeof item.onClick === 'function' ? item.onClick : $.noop;
  const boundClick = onClick.bind(this, name, item.name);
  return (
    <NavItem onClick={boundClick} key={item.key}>{item.name}</NavItem>
  );
}

function dropBtn(name: string) {
  return <a className='btn' style={{width: '100%'}}>{name}</a>;
}

type ModeButtonType = {id?: string, name: string, value: string, modes: Object[]};
function ModeButton({ id, name, value, modes }: ModeButtonType) {
   
  return (
    <div key={name} style={{paddingLeft: '5px', paddingRight: '5px', width: '100%'}}>
      <Dropdown options={{constrainWidth: false}} 
        trigger={ dropBtn(`${name}: ${value}`) }>
          {modes.map(item => getModeButtonElement(name, item))}
      </Dropdown>
    </div>
  );
}

ModeButton.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  value: PropTypes.string.isRequired,
  modes: PropTypes.arrayOf(PropTypes.object).isRequired
};

export default ModeButton;
