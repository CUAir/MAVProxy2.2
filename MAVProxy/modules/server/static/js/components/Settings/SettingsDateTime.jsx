import React from 'react';
import $ from 'jquery';
import PropTypes from 'prop-types';
import dateFormat from 'dateformat';

class SettingsDateTime extends React.Component {

  timeid = null;
  dateid = null;

  componentDidMount(){
    // unfortunately the only way to add the onChanges is here
    $('#' + this.dateid).pickadate()
    $('#' + this.dateid).on('change', this.onDTChange);
    $('#' + this.timeid).pickatime();
    $('#' + this.timeid).on('change', this.onDTChange);
  }

  render(){
    const {id, name, value, onChange} = this.props;

    this.dateid = 'datefield' + name.replace(/ /g, '');
    this.timeid = 'timefield' + name.replace(/ /g, '');

    // split the default value into date and time strings
    const dt = new Date(parseInt(value));
    const time_str = dateFormat(dt, 'hh:MMTT');
    const date_str = dateFormat(dt, 'd mmmm, yyyy'); 

    this.onDTChange = (e) => {
      // So we don't have to import a huge library, this creates a JS parse-able string
      let datestring = $('#' + this.dateid).val() + ', ' + $('#' + this.timeid).val();
      datestring = datestring.replace('PM', ' PM').replace('AM', ' AM');
      onChange(Date.parse(datestring));
    }

    return (
      <div className='col s4'>
        <div className='col s6 input-field' style={{paddingLeft: '0px'}}>
          <input type='text' id={this.dateid} className='datepicker' defaultValue={date_str}/>
          <label htmlFor={this.dateid}>{name}: Date</label>      
        </div>
        <div className='col s6 input-field' style={{paddingRight: '0px'}}>
          <input type='text' id={this.timeid} className='timepicker' defaultValue={time_str} />
          <label htmlFor={this.timeid}>{name}: Time</label>
        </div>
      </div>
    );
  }
}

SettingsDateTime.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  id: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired
};

export default SettingsDateTime;
