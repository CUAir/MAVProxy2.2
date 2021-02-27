// @flow

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import ImmutablePropTypes from 'react-immutable-proptypes';
import CalibrationControlSection from 'js/components/Calibration/CalibrationControlSection';

function mapStateToProps({ calibration: { lines } }) {
  return {
    lines
  };
}

function Line(calibrationLine: string, index: number) {
  return <center key={index}><p>{calibrationLine}</p></center>;
}

function CalibrationSection({ lines }) {
  const padding_style = {padding: '50px'};
  return (
    <div style={{padding: '50px'}}>
      <div className='row'>
        <div className='col s9'>
          <h3><center>MAV Status</center></h3>
          {lines.map(Line)}
        </div>
        <CalibrationControlSection />
      </div>
    </div>
  );
}

CalibrationSection.propTypes = {
  lines: ImmutablePropTypes.listOf(PropTypes.string).isRequired
}

export default connect(mapStateToProps)(CalibrationSection);
