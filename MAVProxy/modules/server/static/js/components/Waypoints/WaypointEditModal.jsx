// @flow

import React from 'react';
import $ from 'jquery';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import { Input, Dropdown, Modal } from 'react-materialize'
import { cellChange } from 'js/actions/WaypointActionCreator';
import WaypointCell from 'js/components/Waypoints/WaypointCell'


function mapStateToProps({ waypoints: { waypoints, selected_wps } }, { onSave, data, units, index, sda }) {
  return {
    wp: waypoints.get(index), data, index, sda, units, wp_len: waypoints.size, selected_wps
  };
}

const getWaypointLocSelector = (index) => (
  <button className='btn-flat' id={`wp-edit-button-${index}`}>
    <i className={`fa fa-pencil`} aria-hidden='true'></i>
  </button>
);

const getWpModalCloseButtons = (n, onSave, onQuit) => {
  return (
    <div>
      <button className='btn-flat modal-action modal-close' id={`msave-${n}`} onClick={onSave} type='submit'>
        save
      </button>
      <button className='btn-flat modal-action modal-close' id={`mquit-${n}`} onClick={onQuit} type='button'>
        cancel
      </button>
    </div>
  );
}

function onWpModalLoad(node) {
  node[0].getElementsByTagName('input')[0].focus()
}

function handleCancelKeyGen(n) {
  return (e) => {
    if (e.keyCode == 27) {
      $(`#mquit-${n}`).click();
    }
  }
}

class WaypointEditModal extends React.Component {

  shouldComponentUpdate(nextProps, nextState) {
    if (this.props.units != nextProps.units) return true;
    if (this.props.data.alt != nextProps.data.alt) return true;
    if (this.props.data.lat != nextProps.data.lat) return true;
    if (this.props.data.lon != nextProps.data.lon) return true;
    if (this.props.data.type != nextProps.data.type) return true;
    if (this.props.data.edit_index != nextProps.data.edit_index) return true;
    if (this.props.index != nextProps.index) return true;
    if (this.props.selected_wps != nextProps.selected_wps) return true;
    return false;
  }

  render() {
    var { onSave, data, units, index, sda, wp, wp_len, selected_wps } = this.props;
    const onWpModalQuit = (node) => {
      if (data.isTemp) return;
      cellChange(index, 'alt', wp.original_alt, sda && data.isTemp);
      cellChange(index, 'lat', wp.original_lat, sda && data.isTemp);
      cellChange(index, 'lon', wp.original_lon, sda && data.isTemp);
      cellChange(index, 'type', wp.original_type, sda && data.isTemp);
    }
    var text_inps = [
      {
        id: 'alt', name: 'Altitude', index: index, wp: wp, value: data.alt,
        sda_temp: sda && data.isTemp, units: units, key: 'alt' + index, min: 0, max: 2000
      },
      {
        id: 'lat', name: 'Latitude', index: index, wp: wp, value: data.lat,
        sda_temp: sda && data.isTemp, units: units, key: 'lat' + index, min: -90, max: 90
      },
      {
        id: 'lon', name: 'Longitude', index: index, wp: wp, value: data.lon,
        sda_temp: sda && data.isTemp, units: units, key: 'lon' + index, min: -180, max: 180
      },
      {
        id: 'type', name: 'Type', index: index, wp: wp, value: data.type,
        sda_temp: sda && data.isTemp, units: units, key: 'type' + index, min: 0, max: 0
      }
    ]

    if (data.isTemp) text_inps.push(
      {
        id: 'num', name: 'Number', index: index, wp: wp, value: data.edit_index,
        sda_temp: sda && data.isTemp, units: units, key: 'num' + index, min: 0, max: wp_len - 1
      })

    return (
      <Modal
        header={
          selected_wps.size > 0
            ? 'Edit Waypoints ' + selected_wps.get(0).index + ' - ' + selected_wps.get(selected_wps.size - 1).index
            : 'Edit Waypoint ' + index
        }
        bottomSheet
        modalOptions={{
          ready: onWpModalLoad,
        }}
        actions={getWpModalCloseButtons(index, () => onSave(data), onWpModalQuit)}
        trigger={getWaypointLocSelector(index)}>
        <div className='row' onKeyDown={handleCancelKeyGen(index)}>
          {text_inps.map(item => <WaypointCell {...item} />)}
        </div>
      </Modal>
    );
  }
}

export default connect(mapStateToProps)(WaypointEditModal);
