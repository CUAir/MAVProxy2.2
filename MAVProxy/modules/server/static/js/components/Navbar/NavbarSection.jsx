// @flow

import $ from 'jquery';
import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import NavbarLinkItem from 'js/components/Navbar/NavbarLinkItem';
import NavbarStatusItem from 'js/components/Navbar/NavbarStatusItem';
import Battery from 'js/components/Navbar/Battery';

import * as StatusActionCreator from 'js/actions/StatusActionCreator';

import { mapResize } from 'js/utils/MapUtils';
import { clickSection, decround, time_to_minutes } from 'js/utils/ComponentUtils';

import { addKeyBindings } from 'js/utils/KeyBindings';

function clickHome() {
  mapResize();
  clickSection('home');
}

const gcsLinks = Object.freeze([
  {name: 'Home', key: 'HOME', onClick: clickHome},
  {name: 'Settings', key: 'SETTINGS', onClick: () => clickSection('settings')},
  {name: 'Parameters', key: 'PARAMETERS', onClick: () => clickSection('parameters')},
  {name: 'Calibration', key: 'CALIBRATION', onClick: () => clickSection('calibration')},
  {name: 'Flight Notes', key: 'FLIGHT_NOTES', onClick: () => clickSection('flightnotes')}
]);

addKeyBindings(Object.freeze([
  {keycode: '1', scope: 'all', action: clickHome},
  {keycode: '2', scope: 'all', action: () => clickSection('settings')},
  {keycode: '3', scope: 'all', action: () => clickSection('parameters')},
  {keycode: '4', scope: 'all', action: () => clickSection('calibration')},
  {keycode: '5', scope: 'all', action: () => clickSection('flightnotes')}
]));

function linkToItems(link, linkNumber) {
  return [
    {name: 'Packet Loss:', value: link.packet_loss, key: `${linkNumber}-packetloss`},
    {name: 'Link Number:', value: link.num, key: `${linkNumber}-num`},
    {name: 'Device:', value: link.device, key: `${linkNumber}-device`},
    {name: 'Num Lost:', value: link.num_lost, key: `${linkNumber}-numlost`},
    {name: 'Link Delay:', value: link.link_delay, key: `${linkNumber}-linkdelay`},
    {name: `${link.device_name} Alive`, value: link.alive, key: `${linkNumber}-alive`}
  ];
}

function mapStateToProps({ status: { safety_switch, armed, links, gps_link, gps_status, 
    in_flight, flight_length, battery, mission_percent, time_to_land, show_ttl }}) {
  return {
    safety_switch, armed, links, gps_link, gps_status, in_flight, flight_length,
    battery, mission_percent, time_to_land, show_ttl
  };
}

function getPlaneStatus({ safety_switch, armed, links, gps_link, gps_status, in_flight, 
    mission_percent, flight_length, time_to_land, show_ttl }) {
  const safetyName = safety_switch ? 'Live' : 'Safe';
  const armedName = armed ? 'Armed' : 'Disarmed';
  const hasNoLinks = links.size === 0;
  const max1Link = links.size <= 1;

  const link1Name = hasNoLinks ? 'Link 1' : links.getIn([0, 'device_name']);
  const link1Alive = hasNoLinks ? false : links.getIn([0, 'alive']);
  const link1Items = hasNoLinks ? [] : linkToItems(links.get(0), 0);
  const link2Name = max1Link ? 'No Link 2' : links.getIn([1, 'device_name']);
  const link2Alive = max1Link ? false : links.getIn([1, 'alive']);
  const link2Items = max1Link ? [] : linkToItems(links.get(1), 1);

  const gpsLinkName = gps_link ? `GPS: ${gps_status} sats` : 'No GPS Link';
  const inFlightName = in_flight ? `In Flight: ${time_to_minutes(flight_length)}` : 'Not In Flight';
  const inFlightFunc = in_flight ? StatusActionCreator.stopFlight : StatusActionCreator.startFlight;

  const flightPercentageName = `Path: ${mission_percent.toFixed(2)}%`;
  const flightTTLName = `TTL: ${time_to_minutes(time_to_land)}`;
  const flightProgressName = show_ttl ? flightTTLName : flightPercentageName;
  const flightProgressStatus = time_to_land > 0;

  return [
    {name: inFlightName, status: in_flight, id: 'IN_FLIGHT', key: 'IN_FLIGHT', onClick: inFlightFunc},
    {name: flightProgressName, status: flightProgressStatus, id: 'FLIGHT_PROGRESS', key: 'FLIGHT_PROGRESS', onClick: StatusActionCreator.toggleShowTTL},
    {name: safetyName, status: safety_switch, id: 'SAFETY_SWITCH', key: 'SAFETY_SWITCH'},
    {name: armedName, status: armed, id: 'ARMED', key: 'ARMED'},
    {name: gpsLinkName, status: gps_link, id: 'GPS_LINK', key: 'GPS_LINK'},
    {name: link1Name, status: link1Alive, id: 'LINK1', key: 'LINK1', half: true, dropdown: true, items: link1Items },
    {name: link2Name, status: link2Alive, id: 'LINK2', key: 'LINK2', half: true, dropdown: true, items: link2Items}
  ];
}

function NavbarSection(props) {
  const { battery } = props;
  const planeStatus = getPlaneStatus(props);
  return (
    <header>
      <div className='navbar-fixed'>
        <nav id='navbar' className='red lighten-2'>
          <div className='nav-wrapper'>
            <div className='row'>
              <div className='col nav-logo' style={{marginRight: '30px', height: '100%'}}>
                <a className='brand-logo' onClick={clickHome} >
                  <img src='img/cuair_logo.png' alt='CUAir'/>
                </a>
              </div>
              <div className='col nav-tabs'>
                <ul className='left'>
                    {gcsLinks.map(link => <NavbarLinkItem {...link} />)}
                </ul>
              </div>
              <div className='col right'>
                <ul id='planeStatus' className='right nav navbar-nav navbar-right'>
                  {planeStatus.map(status => <NavbarStatusItem {...status} />)}
                  <Battery value={battery} />
                </ul>
              </div>
            </div>
          </div>
         </nav>
      </div>
    </header>
  );
}

NavbarSection.propTypes = {
  safety_switch: PropTypes.bool.isRequired,
  armed: PropTypes.bool.isRequired,
  links: PropTypes.any.isRequired,
  gps_link: PropTypes.bool.isRequired,
  gps_status: PropTypes.number.isRequired,
  in_flight: PropTypes.bool.isRequired,
  flight_length: PropTypes.number.isRequired
}

export default connect(mapStateToProps)(NavbarSection)
