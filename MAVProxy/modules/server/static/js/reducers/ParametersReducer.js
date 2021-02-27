import { OrderedMap, Record, List } from 'immutable';

import ParamDocumentation from 'js/utils/ParamDocumentation';
import type { ParametersAction } from 'js/utils/Actions';
import type { ParamType } from 'js/utils/Objects';

const Parameter = Record({
  name: '',
  description: '',
  value: '',
  documentation: '',
  key: '',
  increment: 0,
  units: '',
  isTemp: false,
  values: OrderedMap(),
  originalValue: ''
});

function update_parameter(name: string, value: string, param_map, param_count: number) {
  if (param_map.has(name)) {
    if (param_map.getIn([name, 'value']) === '') param_count++; // only empty for unset parameters
    param_map = param_map.setIn([name, 'value'], value).setIn([name, 'originalValue'], value).setIn([name, 'isTemp'], false);
  } else {
    param_count++;
    const p = new Parameter({name: name, value: value, originalValue: value});
    param_map = param_map.set(name, p);
  }

  return { param_count, param_map };
}

function update_parameters(parameterList: ParamType[], param_map, param_count: number) {
  parameterList.forEach(parameter => {
    ({ param_map, param_count } = update_parameter(parameter.name, parameter.value, param_map, param_count));
  });

  return { param_count, param_map };
}

function edit_parameter(name: string, value: string, param_map) {
  return param_map.has(name) ? param_map.setIn([name, 'value'], value).setIn([name, 'isTemp'], true) : param_map;
}

function load_from_file(original_params, loaded_params) {
  loaded_params.valueSeq().forEach(parameter => {
    const checkbox = document.getElementsByName(`modal-${parameter.name}`);
    if (checkbox.length > 0 && checkbox[0].checked) {
      original_params = edit_parameter(parameter.name, parameter.value, original_params);
    }
  });
  return original_params;
}

function jsToMap(parameterList: ParamType[]) {
  return OrderedMap(List(parameterList).map(Parameter)
    .map(p => p.set('originalValue', p.value))
    .map(p => p.set('values', p.values == undefined ? OrderedMap() : OrderedMap(p.values)))
    .map(p => [p.name, p]));
}

const paramsJS = ParamDocumentation.sort((a, b) => a.name.localeCompare(b.name));
const param_map = jsToMap(paramsJS);

const ParametersState = Record({
  param_map: param_map,
  param_count: 0,
  param_max_count: 0,
  selected: '',
  loaded_params: param_map,
  note: '',
  search_field: '',
  modal_open: false
});

const initialState = new ParametersState();

export default function parametersReducer(state: any = initialState, action: ParametersAction) {
  switch (action.type) {
  case 'RECEIVE_SINGLE_PARAMETER': {
    const { param_map, param_count } = update_parameter(action.name, action.value, state.param_map, state.param_count);
    return state
      .set('param_map', param_map)
      .set('param_count', param_count);
  }
  case 'RECEIVE_MULTIPLE_PARAMETERS': {
    const { param_map, param_count } = update_parameters(action.parameters, state.param_map, state.param_count);
    return state
      .set('param_map', param_map)
      .set('param_count', param_count);
  }
  case 'RECEIVE_MAX_PARAM_COUNT':
    return state
      .set('param_max_count', action.count);
  case 'EDIT_PARAMETER':
    return state
      .set('param_map', edit_parameter(action.name, action.value, state.param_map));
  case 'SELECT_PARAMETER':
    return state
      .set('selected', action.name);
  case 'PARAMETER_LOAD_FROM_FILE':
    return state
      .set('loaded_params', jsToMap(action.parameters));
  case 'RECEIVE_NOTE':
    return state
      .set('note', action.note);
  case 'RECEIVE_SEARCH_FIELD':
    return state
      .set('search_field', action.search_field);
  case 'RECEIVE_MODAL_OPEN':
    return state
      .set('modal_open', action.open);
  case 'PARAMETER_SAVE_FROM_MODAL':
    return state
      .set('param_map', load_from_file(state.param_map, state.loaded_params));
  case 'RESET_PARAM_COUNT':
    return state
      .set('param_count', 0);
  default:
    return state;
  }
}
