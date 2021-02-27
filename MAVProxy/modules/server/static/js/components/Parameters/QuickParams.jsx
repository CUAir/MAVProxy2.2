// @flow

import React from 'react';
import $ from 'jquery';
import { OrderedMap } from 'immutable';
import ImmutablePropTypes from 'react-immutable-proptypes';
import { Input } from 'react-materialize';
import _ from 'lodash';

import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';

import { sendParameter } from 'js/utils/SendApi';

const iToSwitch = Object.freeze({
  '1': 'FURTHEST',
  '2': 'MIDDLE',
  '3': 'CLOSEST'
});

function _onValChange(p, e) {
  const val = !isNaN(parseFloat(e)) ? e : e.target.value;

  if (p.range !== undefined) {
    const range = p.range.split(' ').map(parseFloat);
    if ((val > range[1] && range[1] > 0) || (val < range[0] && range[0] < 0)) {
      return;
    }
  }

  ParametersActionCreator.editParameter(p.name, val);
}

function _onFltModeChange(i, e, param_map, valueMap) {
  const val = e.target.value;
  const fltMode1 = `FLTMODE${i*2 - 1}`;
  const fltMode2 = `FLTMODE${i*2}`;
  const flippedValueMap = OrderedMap(valueMap.entrySeq().map(pair => [pair[1], pair[0]]));

  ParametersActionCreator.editParameter(fltMode1, parseInt(flippedValueMap.get(val)));
  sendParameter(param_map.get(fltMode1).set('value', parseInt(flippedValueMap.get(val))));

  ParametersActionCreator.editParameter(fltMode2, flippedValueMap.get(val));
  sendParameter(param_map.get(fltMode2).set('value', parseInt(flippedValueMap.get(val))));
}

function QuickDropdown({ param_map, i }) {
  const p1 = param_map.get(`FLTMODE${i*2 - 1}`);
  const p2 = param_map.get(`FLTMODE${i*2}`);
  return (
    <div className='col s4' style={{paddingLeft: '0px', paddingRight: '0px'}}>
      <Input
        type='select'
        label={iToSwitch[i]}
        value={p1.values.get(p1.value + '')}
        className={p1.isTemp || p2.isTemp ? 'red-dropdown' : 'black-dropdown'}
        onChange={e => _onFltModeChange(i, e, param_map, p1.values)}>
        {p1.values.valueSeq().map(item => <option key={item}>{item}</option>)}
      </Input>
    </div>
  );
}

type QuickNumberType = {name: string, value: string, isTemp: bool, onChange: Function};
function QuickNumber({ isTemp, name, value, onChange = $.noop }: QuickNumberType) {
  let formid = 'quick-number-' + name.replace(/ /g, '');
  return (
    <div className='input-field'>
      <input
        id={formid}
        type='number'
        value={value}
        style={{color: isTemp ? 'red' : 'black'}}
        onChange={onChange} />
      <label htmlFor={formid} className='active'>{name}</label>
    </div>
  );
}

const quicks = new Set(['TRIM_ARSPD_CM', 'LIM_ROLL_CD', 'THR_MIN', 'THR_MAX', 'TECS_PITCH_MAX', 'TECS_PITCH_MIN']);

function getQuickParams(param_map) {
  return param_map
    .map(p => quicks.has(p.name) ? p : null)
    .filter(p => p !== null);
}

function QuickParams({ param_map }: {param_map: Object}) {
  const filtered = getQuickParams(param_map);
  const textFields = filtered.toList().map(p => 
    <div className="col s12" key={`quick-number-div-${p.name}`}>
      <QuickNumber
        onChange={e => _onValChange(p, e)}
        value={p.value}
        isTemp={p.isTemp}
        name={p.name} />
    </div>
  );

  return (
    <div>
      <h5 style={{marginBottom: '0px', textAlign: 'center'}}>Quick Params</h5>
      {_.range(1, 4).map(i => <QuickDropdown key={`quick-dropdown-${i}`} param_map={param_map} i={i} />)}
      {textFields}
    </div>
  );
}

QuickParams.propTypes = {
  param_map: ImmutablePropTypes.orderedMap.isRequired
};

export default QuickParams;
