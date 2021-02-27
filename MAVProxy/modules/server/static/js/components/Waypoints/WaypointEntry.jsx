//

import React from 'react';
import { connect } from 'react-redux';

import { SortableHandle } from 'react-sortable-hoc';
import { Input, Dropdown, Modal } from 'react-materialize'

import { cellChange, confirmSelect, sendAllWaypoints, setSelectedSda, setSelected, clearSelected, updateItem } from 'js/actions/WaypointActionCreator';
import WaypointEditModal from 'js/components/Waypoints/WaypointEditModal';
import WaypointTypeSelector from 'js/components/Waypoints/WaypointTypeSelector';
import { mToFt, ftToM, decround } from 'js/utils/ComponentUtils';

const wp_types = Object.freeze({
  16: { name: 'WAYPOINT', icon: 'map-marker' },
  17: { name: 'LOITER', icon: 'paper-plane' },
  177: { name: 'DO JUMP', icon: 'undo' },
  20: { name: 'RTL', icon: 'home' },
  21: { name: 'LAND', icon: 'angle-double-down' },
  22: { name: 'TAKEOFF', icon: 'angle-double-up' }
});


function mapStateToProps({ waypoints: { current_waypoint, selected_sda,
  selected_row, selected_wps }, settings: { sdaMode } }, { units, data, index, sda }) {
  return {
    current: current_waypoint,
    selected_sda, selected_row, data, index, sda, units, sdaMode, selected_wps
  };
}

function dragHandle(icon, isTemp) {
  handclass = 'inline-bl'
  style = { color: 'black' };
  if (isTemp) {
    var handclass = 'inline-bl hand';
    var style = { color: 'red' };
  }
  const handle = () => (
    <div className={handclass} style={{ width: '30px', paddingLeft: '10px' }}>
      <i className={`fa fa-${icon}`} aria-hidden='true' style={style}></i>
    </div>
  );
  const DisabledHandle = handle;
  return <DisabledHandle />;
}


class WaypointEntry extends React.Component {

  render() {
    var { sdaMode, current, data, selected_sda, selected_row, index,
      sda, units, baseAltitude, list_index, selected_wps } = this.props;
    var wp_data = data.toJS(); //TODO: this might be inefficient
    if (!units) {
      wp_data.alt = mToFt(data.alt);
      wp_data.min_dist = mToFt(data.min_dist);
      wp_data.original_alt = mToFt(data.original_alt);
    }
    wp_data.alt = decround(wp_data.alt, 2);
    wp_data.original_alt = decround(wp_data.original_alt, 2);
    let backgroundColor;
    let selected_wps_idx = selected_wps.map(wp => wp.index);

    if (data['isSda']) backgroundColor = 'purple lighten-4';
    else if (!sdaMode && (selected_row == index)) backgroundColor = 'blue lighten-4';
    else if (sdaMode && (selected_sda == index)) backgroundColor = 'blue lighten-4';
    else if (selected_wps_idx.includes(index)) backgroundColor = 'blue lighten-4';
    else if (data['number'] == -1) backgroundColor = 'white';
    else if (current < data['number']) backgroundColor = 'white';
    else if (current > data['number']) backgroundColor = 'grey lighten-3';
    else backgroundColor = 'green lighten-3';

    const style = { backgroundColor: backgroundColor, width: '100%' };
    const modal_id = `wp-edit-modal-id-${data.number}`;

    const handle = dragHandle(wp_types[data.type].icon, data.isTemp);
    const mindist = wp_data.min_dist > 99 ? ">99" : decround(wp_data.min_dist, 1)

    function onBGClick(sda, number) {
      sda ? setSelectedSda(number) : setSelected(number);
    }

    function onWpModalSave(modal_data) {
      if (modal_data.edit_index != modal_data.index) {
        console.log(modal_data)
        updateItem(modal_data.edit_index, modal_data.index)
      }
      if (!data.isTemp)
        sendAllWaypoints();
    }
    return (
      <li id={"wp_entry" + index.toString()} key={data.number.toString()} className={'dividers ' + backgroundColor} onClick={() => onBGClick(sda, index)}>
        {handle}
        <div className='inline-bl pointer' style={{ width: '40px' }}>
          {data.number}
        </div>

        <div className='inline-bl alt-txt' style={{ width: '60px' }}>
          {data.isTemp ? wp_data.alt : wp_data.original_alt}{units ? 'm' : 'ft'}
        </div>

        <div className='inline-bl min-dist-txt' style={{ width: '50px' }}>
          {mindist}{units ? 'm' : 'ft'}
        </div>

        <div className='inline-bl' style={{ width: '80x' }}>
          <WaypointEditModal
            data={wp_data}
            units={units}
            onSave={onWpModalSave}
            index={index}
            sda={sda}
          />
        </div>
        <div className='inline-bl' style={{ width: '20px' }}>
          ({list_index})
          </div>
      </li>
    );
  }
}
// <WaypointTypeSelector sda={sda} data={data} index={index} />

export default connect(mapStateToProps)(WaypointEntry);
