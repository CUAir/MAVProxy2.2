// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { MiniParamType, ParamType } from 'js/utils/Objects';

/**
 * @module actions/ParametersActionCreator
 */

/**
 * Sets a single parameter
 * @param {string} name
 * @param {NValue} value
 * @returns {undefined}
 */
export function receiveSingleParameter(name: string, value: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SINGLE_PARAMETER',
    name, value
  });
}

/**
 * Sets multiple parameters
 * @param {Parameter[]} parameters
 * @returns {undefined}
 */
export function receiveMultipleParameters(parameters: MiniParamType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MULTIPLE_PARAMETERS',
    parameters
  });
}

/**
 * Sets the max parameter count
 * @param {number} count
 * @returns {undefined}
 */
export function receiveMaxParamCount(count: number): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MAX_PARAM_COUNT',
    count
  });
}

/**
 * Edits the value of a parameter
 * @param {string} name
 * @param {NValue} value
 * @returns {undefined}
 */
export function editParameter(name: string, value: number): void {
  return GlobalStore.dispatch({
    type: 'EDIT_PARAMETER',
    name, value
  });
}

/**
 * Edits list of parameters
 * @param {Parameter[]} parameters
 * @returns {undefined}
 */
export function loadParametersFromFile(parameters: ParamType[]): void {
  return GlobalStore.dispatch({
    type: 'PARAMETER_LOAD_FROM_FILE',
    parameters
  });
}

/**
 * Sets a parameter as selected
 * @param {string} name
 * @returns {undefined}
 */
export function selectParameter(name: string): void {
  return GlobalStore.dispatch({
    type: 'SELECT_PARAMETER',
    name
  });
}

/**
 * Changes the note value in the store/display
 * Used when downloading parameters
 * @param {boolean} note
 * @returns {undefined}
 */
export function receiveNote(note: string): void { 
  return GlobalStore.dispatch({
    type: 'RECEIVE_NOTE',
    note
  });
}

/**
 * Changes the value of the parameter search field
 * @param {string} search_field
 * @returns {undefined}
 */
export function receiveSearchField(search_field: string): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SEARCH_FIELD',
    search_field
  });
}

/**
 * Changes whether the parameter modal is open
 * @param {boolean} open
 * @returns {undefined}
 */
export function receiveModalOpen(open: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_MODAL_OPEN',
    open
  });
}

/**
 * Tells the parameter store to save all of the selected parameters
 * @returns {undefined}
 */
export function saveParamModal(): void {
  return GlobalStore.dispatch({
    type: 'PARAMETER_SAVE_FROM_MODAL'
  });
}
