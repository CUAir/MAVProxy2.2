// 

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';

import ParamModal from 'js/components/Parameters/ParamModal';
import QuickParams from 'js/components/Parameters/QuickParams';

import { BUTTON, FILE_INPUT, TEXT_INPUT } from 'js/constants/ButtonTypes';
import { EPSILON } from 'js/constants/Frequency';

import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';

import { saveParamsToFile } from 'js/utils/DownloadApi';
import { loadParamsFromFile } from 'js/utils/LoadApi';
import { sendParameter, sendAllParameters } from 'js/utils/SendApi';
import { initializeParameters } from 'js/utils/ReceiveApi';

function getParameterControls(search_field, note, selected, param_map) {
  const param_controls = [
    {text: 'Send', type: BUTTON, color: 'success', key: 'SEND_PARAM', onClick: () => sendParameter(param_map.get(selected).toJS())},
    {text: 'Send All', type: BUTTON, color: 'success', key: 'SEND_ALL_PARAMS', onClick: () => sendAllParameters(param_map.valueSeq().toJS())},
    {text: 'Refresh', type: BUTTON, color: 'unknown', key: 'REFRESH_PARAMS', onClick: initializeParameters},
    {text: 'Load From File', type: FILE_INPUT, color: 'unknown', id: 'LOAD_PARAMS_FROM_FILE', key: 'LOAD_PARAMS_FROM_FILE', onClick: loadParamsFromFile},
    {text: 'Save To File', type: BUTTON, color: 'unknown', key: 'SAVE_PARAMS_TO_FILE', onClick: () => saveParamsToFile(note, param_map.valueSeq().toJS())}
  ];

  const searchField = [{text: 'Search', type: TEXT_INPUT, value: search_field, key: 'SEARCH_PARAM',
    onChange: e => ParametersActionCreator.receiveSearchField(e.nativeEvent.target.value)}];
  const noteField = [{text: 'Note', type: TEXT_INPUT, value: note, key: 'NOTE_PARAM',
    onChange: e => ParametersActionCreator.receiveNote(e.nativeEvent.target.value)}];

  return searchField.concat(param_controls, noteField);
}

function getProgress(param_count, param_max_count) {
  return {
    key: 'PARAMETER_PROGRESS', value: param_count, max: param_max_count
  };
}

function diffParams(params, loaded_params) {
  return loaded_params.map(loaded_param => {
    const matchParam = params.find(param => param.name === loaded_param.name);
    const paramValue = matchParam !== undefined ? matchParam.value : null;
    const loadedValue = loaded_param.value;
    const same = (paramValue === null || loadedValue === '' || Math.abs(paramValue - loadedValue) < EPSILON);
    return same ? null : {name: loaded_param.name, old: paramValue, new: loadedValue};
  }).filter(diff => diff != null);
}

function mapStateToProps({ parameters: { search_field, note, selected, param_map,
    param_count, param_max_count, modal_open, loaded_params } }) {
  return {
    search_field, note, selected, param_map, param_count: parseInt(param_count),
    param_max_count: parseInt(param_max_count), modal_open, loaded_params 
  };
}

function getActionElement(item) {
  let elem;
  switch (item.type) {
    case BUTTON:
      elem = (
        <button className='btn' onClick={item.onClick} style={{width: '100%'}}>
          {item.text}
        </button>
      );
      break;
    case FILE_INPUT:
      elem = ( 
        <div className='file-field' key={item.key} style={{paddingTop: '6px', paddingBottom: '2px'}}>
          <div className='btn' style={{width: '100%'}}>
            <span>{item.text}</span>
            <input type='file' accept='.p,.param' onChange={e => {loadParamsFromFile(e); e.target.value = ''}} />
          </div>
          <div className='file-path-wrapper' style={{width: '0px', height: '0px'}}>
            <input className='file-path validate' accept='.p' type='text' style={{width: '0px', height: '0px'}} />
          </div>
        </div>
      );
      break;
    case TEXT_INPUT:
      elem = (
      <div className='input-field' style={{margin: '5px'}} key={item.key}>
        <input
          id={'param-textinp-' + item.key}
          type='text'
          defaultValue={item.value}
          onChange={item.onChange}
        />
        <label htmlFor={'param-textinp-' + item.key} className='active'>{item.text}</label>
      </div>
      );
      break;
    default:
      elem = <div />;
      break;
  }

  return (
    <div key={item.key} style={{paddingLeft: '5px', paddingRight: '5px', width: '100%'}}>
      {elem}
    </div>
  );
}


function ParametersControlSection({ search_field, note, selected, param_map,
    param_count, param_max_count, modal_open, loaded_params }) {
  const controls = getParameterControls(search_field, note, selected, param_map);
  const diff = diffParams(param_map.valueSeq(), loaded_params.valueSeq());

  return (
    <ul id='param-edit-nav' className='side-nav right-aligned fixed collection with-header'>
      <li className='collection-header'>
        <h5>Parameter Controls</h5>
      </li>
      <li>
        {controls.map(getActionElement)}
      </li>
      <li>
        <QuickParams param_map={param_map} />
      </li>
      <ParamModal open={modal_open} diff={diff} />
    </ul>
  );
}

ParametersControlSection.propTypes = {
  search_field: PropTypes.string.isRequired,
  note: PropTypes.string.isRequired,
  selected: PropTypes.string.isRequired,
  param_map: ImmutablePropTypes.orderedMap.isRequired,
  param_count: PropTypes.number.isRequired,
  param_max_count: PropTypes.number.isRequired,
  modal_open: PropTypes.bool.isRequired,
  loaded_params: ImmutablePropTypes.orderedMap.isRequired
};

export default connect(mapStateToProps)(ParametersControlSection);
