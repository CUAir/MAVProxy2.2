// @flow

import React from 'react';
import { SortableContainer, SortableElement, arrayMove } from 'react-sortable-hoc';

import WaypointEntry from 'js/components/Waypoints/WaypointEntry';


const WaypointItem = SortableElement(({value}) => {
  return (
    <WaypointEntry 
      sda={value.sda} 
      baseAltitude={value.baseAltitude} 
      units={value.units} 
      data={value.data} 
      index={value.index}
      list_index={value.list_index} />
  );
});

const WaypointListContainer = SortableContainer(({items}) => {
  return (
    <ul className='wp-list' id='wp-list'>
      {items.map((value, index) => {
        value.list_index = index;
        return (<WaypointItem key={`wp-${index}`} index={index} value={value} />)
        })
      }
    </ul>
  );
});

class WaypointList extends React.Component {
  
  // update the state after a re-order
  onSortEnd = ({oldIndex, newIndex} : Object) => {
    this.props.reorder(newIndex, oldIndex);
  };


  render() {
    const items = this.props.wps.map((wp, index) => ({
      sda: this.props.sda, 
      baseAltitude: this.props.baseAltitude, 
      units: this.props.units, 
      data: wp, 
      index: index
    }));

    return <WaypointListContainer items={items} onSortEnd={this.onSortEnd} useDragHandle={true} />;
  }
}

export default WaypointList;
