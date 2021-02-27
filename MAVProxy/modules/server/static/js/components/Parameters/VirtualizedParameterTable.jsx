import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import { Record } from 'immutable';
import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';
import { Input } from 'react-materialize'

import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';
import { Column, Table } from 'react-virtualized'

const show_not_loaded = true;

function getSearchedParameters(search_field, param_map) {
  const search_lowercase = search_field.toLowerCase();
  return param_map.valueSeq().filter(param => {
    return (param.name.toLowerCase().includes(search_lowercase) ||
      param.description.toLowerCase().includes(search_lowercase) ||
      param.documentation.toLowerCase().includes(search_lowercase)) &&
      (show_not_loaded || param.value != '');
  });
}

function mapStateToProps({ settings, parameters: { search_field, param_map, selected } }) {
  return {
    param_map, search_field, selected
  };
}

function getParametersItem(selected) {
  return (item) => {
    function _onValChange(e) {
      const val = !isNaN(parseFloat(e)) ? e : e.target.value;

      if (item.range !== undefined) {
        const range = item.range.split(' ').map(parseFloat);
        if ((val > range[1] && range[1] > 0) || (val < range[0] && range[0] < 0)) {
          return;
        }
      }

      // if (item.increment !== undefined) {
      //   const divided = val / parseFloat(item.increment);
      //   if (parseInt(divided) !== divided && !isNaN(parseFloat(item.increment))) {
      //     return;
      //   }
      // }

      ParametersActionCreator.editParameter(item.name, val);
    }    

    let color;
    if (selected === item.name) color = 'blue lighten-4';
    else if (item.value === '') color = 'grey lighten-4';
    else color = 'white';
    return {
        name: item.name,
        description: item.description,
        value: item.value,
        units: item.units,
        values: item.values,  
        documentation: item.documentation,
        increment: item.increment,
        isTemp: item.isTemp,
        color: color,
        onChange: _onValChange,
        id: item.name,
        key: item.name,
        onClick: () => ParametersActionCreator.selectParameter(item.name)
    };
  }
}

function getValueColumn({ cellData, rowData}) {
  var { id, values, onChange, value, isTemp, increment,
    color, name, units, description, documentation, onClick } = rowData;

  const inputValue = value.toString().substring(0, 6);
  const itemid = 'param-item-' + id.replace(/ /g, '-');
  const text_color = isTemp ? 'red-text' : 'black-text';
  if (values.size > 0) {
    return (
      <div className='param-text-wrap' style={{margin: '10px 20px', width: '220px'}}>
        <Input
          type='select'
          value={value + ''}
          className={text_color}
          onChange={(e) => {onChange(e.target.value)}}>
          {values.keySeq().map(k => (
            <option key={k} value={k}>
              {values.get(k)}
            </option>
          ))}
        </Input>
      </div>
    );
  } else {
    const step = increment ? parseFloat(increment) : 1;
    return (
      <div style={{margin: '10px 20px', overflow: 'hidden', width: '200px'}}>
        <div className='input-field '>
          <input
            id={'inp-' + itemid}
            type='number'
            className={text_color}
            value={inputValue}
            onChange={onChange}
            name={name}
            step={step}
          />
          <label htmlFor={'inp-' + itemid} className='active'>{units}</label>
        </div>
      </div>
    );
  }
}

function renderTextCell({ cellData, rowData }) {
  var cell_class = 'inline-bl valign-wrapper';
  return (
    <div className={cell_class} onClick={rowData.onClick} style={{height: '100%'}}>
      <span>{cellData}</span>
    </div>
  );
}

const toolbar_height = 65; // pixel padding from the top
const sidenav_width = 300; // pixel padding from the side

class VirtualizedParameterTable extends React.Component {
  constructor(props) {
    super(props);
    this.divheight = $(window).height() - toolbar_height;
    this.divwidth = $(window).width() - sidenav_width;
  }

  componentDidMount() {
    this.divheight = $(window).height() - toolbar_height;
    this.divwidth = $(window).width() - sidenav_width;
  }

  render() {
    var { search_field, param_map, selected } = this.props;
    const parameters = getSearchedParameters(search_field, param_map)
      .map(getParametersItem(selected)).toJS();
    const name_w = 200; // width of the name column
    const description_w = 200; // width of the description column
    const value_w = 300; // width of the value column
    const margin_w = 40; // amount of space to leave for margins at the end of the row
    const documentation_w = this.divwidth - name_w - description_w - value_w - margin_w;

    const getRowClass = ({ index }) => {
      if (index == -1) {
        return 'white list-row-header';
      }
      let rowdata = parameters[index];
      return 'list-row ' + rowdata.color;
    }

    const getRowHeight = ({ index }) => {
      const char_w = 7.0; // width of one character
      const char_h = 25; // height of one character
      const margin = 20; // padding within the row applied to all rows
      const min_row_height = 100; // absolute minimum value for each row
      let rowdata = parameters[index];
      return Math.max(min_row_height, char_h * Math.ceil((rowdata.documentation.length)/(documentation_w/char_w)) + margin);
    }

    const onRowClick = ({event, rowData}) => rowData.onClick(event);

    return (
      <div id='parametersDiv' className='parameter-main'>
        <Table
          width={this.divwidth}
          height={this.divheight}
          headerHeight={35}
          headerClassName='param-list-header-cell'
          rowHeight={getRowHeight}
          rowClassName={getRowClass}
          rowCount={parameters.length}
          onRowClick={onRowClick}
          gridClassName='param-list'
          id='param-list'
          rowGetter={({ index }) => parameters[index]}>
          <Column
            label='Name'
            dataKey='name'
            width={name_w}
            className='inline-bl'
            headerStyle={{width: name_w + 'px'}}
            style={{width: name_w + 'px', height: '100%'}}
            cellRenderer={renderTextCell}
          />
          <Column
            width={description_w}
            label='Description'
            dataKey='description'
            className='inline-bl'
            headerStyle={{width: description_w + 'px'}}
            style={{width: description_w + 'px', height: '100%'}}
            cellRenderer={renderTextCell}
          />
          <Column
            width={value_w}
            label='Value'
            dataKey='value'
            className='inline-bl param-val-col'
            headerStyle={{width: value_w + 'px', paddingLeft: '20px'}}
            style={{width: value_w + 'px', height: '100%'}}
            cellRenderer={getValueColumn}
          />
          <Column
            width={documentation_w}
            label='Documentation'
            dataKey='documentation'
            className='inline-bl'
            style={{width: documentation_w + 'px', height: '100%'}}
            cellRenderer={renderTextCell}
          />
        </Table>
      </div>
    );
  }
}

VirtualizedParameterTable.propTypes = {
  search_field: PropTypes.string.isRequired,
  selected: PropTypes.string.isRequired,
  param_map: ImmutablePropTypes.orderedMap.isRequired
};

export default connect(mapStateToProps)(VirtualizedParameterTable);
