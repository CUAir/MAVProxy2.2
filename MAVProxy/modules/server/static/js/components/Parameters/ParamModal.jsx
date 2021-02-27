import React from 'react';
import autobind from 'autobind-decorator';
import { Input, Modal } from 'react-materialize'
import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';

import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';

const modalClass = 'modal-checkbox';

type diffObjectType = {name: string, old: number, new: number};

function makeDiff(diffObject: diffObjectType) {
  return (
    <tr key={diffObject.name}>
      <td>
        <input type='checkbox' className='modal-checkbox' name={`modal-${diffObject.name}`}
          id={`modal-check-${diffObject.name}`} defaultChecked={true}/>
        <label htmlFor={`modal-check-${diffObject.name}`}> </label>
      </td>
      <td>{diffObject.name}</td>
      <td>{diffObject.old}</td>
      <td>{diffObject.new}</td>
    </tr>
  );
}

function checkAll() {
  Array.prototype.forEach.call(
    document.getElementsByClassName(modalClass),
    checkbox => checkbox.checked = true
  );
}

function uncheckAll() {
  Array.prototype.forEach.call(
    document.getElementsByClassName(modalClass),
    checkbox => checkbox.checked = false
  );
}

function hideModal() {
  ParametersActionCreator.receiveModalOpen(false);
  checkAll();
}

function save() {
  ParametersActionCreator.saveParamModal();
}

const getWpModalCloseButtons = () => {
  return (
    <div>
      <button className='btn-flat modal-action modal-close' id={`param-modal-save`} onClick={save} type='submit'>
        save
      </button>
      <button className='btn-flat modal-action modal-close' id={`param-modal-quit`} type='button'>
        cancel
      </button>
    </div>
  );
}

type ParamModalType = {open: boolean, diff: diffObjectType[]};
class ParamModal extends React.Component {

  shouldComponentUpdate (nextProps, nextState) {
    // sketchy... worst case scenario, compare this.props.diff as well
    if(this.props.open != nextProps.open) return true;
    return false;
  }

  componentDidUpdate(prevProps, prevState) {
    if(this.props.open && !prevProps.open) {
      $('#param-diff-modal').modal('open');
    }
  }

  render() {
    const {open, diff, loaded_params} = this.props;
    return (
      <Modal 
        header='Parameter Load Difference'
        modalOptions={{
          complete: hideModal
        }}
        actions={getWpModalCloseButtons()}
        fixedFooter
        id='param-diff-modal'>
          <div>
            <button className='btn' style={{margin: '5px'}} onClick={checkAll}>Check All</button>
            <button className='btn' style={{margin: '5px'}} onClick={uncheckAll}>Uncheck All</button>
          </div>
          <div>
            <table className='table'>
              <thead>
                <tr>
                  <th>Use?</th>
                  <th>Name</th>
                  <th>Original Value</th>
                  <th>New Value</th>
                </tr>
              </thead>
              <tbody>
                {diff.map(makeDiff)}
              </tbody>
            </table>
          </div>
      </Modal>
    );
  }
}

ParamModal.propTypes = {
  open: PropTypes.bool.isRequired,
  diff: ImmutablePropTypes.seq.isRequired
}

export default ParamModal;
