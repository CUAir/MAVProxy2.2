import React from 'react';

import { Dropdown } from 'react-materialize'

import { cellChange, confirmSelect, sendWaypoint } from 'js/actions/WaypointActionCreator';

const wp_types = Object.freeze({
  16: {name: 'WAYPOINT', icon: 'map-marker'},
  17: {name: 'LOITER', icon: 'paper-plane'},
  177: {name: 'DO JUMP', icon: 'undo'},
  20: {name: 'RTL', icon: 'home'}, 
  21: {name: 'LAND', icon: 'angle-double-down'},
  22: {name: 'TAKEOFF', icon: 'angle-double-up'}
});

const getWaypointTypeButton = (val) => {
  return (
    <button className='btn-flat icon-button'>
      <i className={`fa fa-${wp_types[val].icon}`} />
      <i className='fa fa-caret-down' aria-hidden='true' style={{paddingLeft: '5px', fontSize: '12px'}}></i>
    </button>
  );
}

function WaypointTypeSelector({ data, index, sda }) {

  function onTypeClick(wp_type) {
    cellChange(index, 'type', parseInt(wp_type), sda && data.isTemp);
    if (!data.isTemp) sendWaypoint();
  }
  
  return (
    <div>
      <Dropdown options={{constrainWidth: false}} trigger={
        getWaypointTypeButton(data.type)
      }>
        <ul>
          {Object.keys(wp_types).map(k => (
            <li>
              <a onClick={() => onTypeClick(k)}>
                <i className={`fa fa-${wp_types[k].icon}`} />
                {wp_types[k].name}
              </a>
            </li>
          ))}
        </ul>
      </Dropdown>
    </div>
  );
}

export default WaypointTypeSelector;
