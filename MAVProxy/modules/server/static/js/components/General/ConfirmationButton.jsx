import React from 'react';
import { Modal } from 'react-materialize'

const getModalCloseButtons = (onConfirm, onCancel) => {
  return (
    <div>
      <button className='btn-flat modal-action modal-close' onClick={onCancel}>
        cancel
      </button>
      <button className='btn-flat modal-action modal-close' onClick={onConfirm}>
        confirm
      </button>
    </div>
  );
}

function ConfirmationButton({ name, confirmation_text, onConfirm, onCancel, children }) {

  function onModalLoad(node) {
    node[0].getElementsByTagName('button')[0].focus()
  }

  return (
    <Modal 
      header={name}
      modalOptions={{
        ready: onModalLoad,
        complete: onCancel
      }}
      actions={getModalCloseButtons(onConfirm, onCancel)}
      trigger={children}>
      <div>
        <p className='flow-text'>{confirmation_text}</p>
      </div>
    </Modal>
  );
}

export default ConfirmationButton;
