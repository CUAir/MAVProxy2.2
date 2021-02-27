// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { receiveScratchpad } from 'js/actions/SettingsActionCreator';

import FlightCard from 'js/components/FlightNotes/FlightCard';

function mapStateToProps({ settings: { scratchpad } }) {
  return {
    scratchpad
  };
}

function Scratchpad({ scratchpad }) {
  return (
    <div className='container'>
      <FlightCard />
      <div className='divider' />
      <div className='row'>
        <div className='input-field col s12' style={{marginTop: '30px'}}>
          <textarea 
            className='materialize-textarea'
            onChange={e => receiveScratchpad(e.nativeEvent.target.value)}
            value={scratchpad}
            id='scratchpad-field' />
          <label className='active' htmlFor='scratchpad-field'>Scratchpad (don't put flight stuff here)</label>
        </div>
      </div>
    </div>
  );
}

Scratchpad.propTypes = {
  scratchpad: PropTypes.string.isRequired
};

export default connect(mapStateToProps)(Scratchpad);
