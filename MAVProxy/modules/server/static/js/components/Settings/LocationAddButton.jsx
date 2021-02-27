import React from 'react';
import { Modal } from 'react-materialize'
import { addLocation } from 'js/utils/SendApi';

const getModalCloseButtons = (onConfirm) => {
  return (
    <div>
      <button className='btn-flat modal-action modal-close' onClick={onConfirm} type='submit'>
        save
      </button>
      <button className='btn-flat modal-action modal-close' type='button'>
        cancel
      </button>
    </div>
  );
}

const getModalOpenButton = () => (
  <button className='btn'>
    Add Location
  </button>
);

class LocationAddButton extends React.Component {

  constructor(props) {
    super(props);
    this.data = {
      name: 'White Square',
      lat: 0,
      lng: 0,
      zoom: 17
    }
  }

  render(){
    function onModalLoad(node) {
      node[0].getElementsByTagName('input')[0].focus()
    }

    return (
      <div className='col input-field s4'>
        <Modal 
          header='Add a new map location'
          modalOptions={{
            ready: onModalLoad
          }}
          actions={getModalCloseButtons(() => addLocation(this.data))}
          trigger={getModalOpenButton()}>

          <div className='row'>
            <div className='input-field col s5'>
              <input placeholder='Neno International Airport' id='loc-add-name' type='text'
                  onChange={(e) => this.data.name = e.target.value.replace(/ /g, '_')} />
              <label htmlFor='first_name'>Location Name</label>
            </div>
            <div className='input-field col s3'>
              <input placeholder='42.4473054' id='loc-add-lat' type='number' 
                  onChange={(e) => this.data.lat = parseFloat(e.target.value)} />
              <label htmlFor='first_name'>Latitude</label>
            </div>
            <div className='input-field col s3'>
              <input placeholder='-76.612611' id='loc-add-lon' type='number' 
                  onChange={(e) => this.data.lng = parseFloat(e.target.value)} />
              <label htmlFor='first_name'>Longitude</label>
            </div>
          </div>

        </Modal>
      </div>
    );
  }
}

export default (LocationAddButton);
