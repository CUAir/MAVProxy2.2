// @flow

import React from 'react';
import PropTypes from 'prop-types';

const outerstyle = {width: '100%'};

type ProgressBarType = {value: number, max: number};
function ProgressBar({ value, max }: ProgressBarType) {

  const v = Math.min(value, max);
  const pctReceived = max === 0 ? -1 : 100 * v / max;
  const innerstyle = {width: `${Math.min(pctReceived, 100)}%`};
  return (
    <div style={{paddingLeft: '5px', paddingRight: '5px', width: '100%'}}>
      <div className='progress'>
          <div className='determinate' style={innerstyle}></div>
      </div>
      <h5 className='center-align'>
        {v} / {max}
      </h5>
    </div>
  );
}

ProgressBar.propTypes = {
  value: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired,
  max: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired
};

export default ProgressBar;
