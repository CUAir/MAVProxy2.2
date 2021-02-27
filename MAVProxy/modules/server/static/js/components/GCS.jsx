// @flow

import React from 'react';
import $ from 'jquery';
import { Provider } from 'react-redux';

import NavbarSection from 'js/components/Navbar/NavbarSection';
import PlaneInfoSection from 'js/components/PlaneInfo/PlaneInfoSection';
import MapSection from 'js/components/Map/MapSection';
import Slider from 'js/components/Map/Slider';
import PlaneActionSection from 'js/components/PlaneAction/PlaneActionSection';
import WaypointContainer from 'js/components/Waypoints/WaypointContainer';
import SettingsSection from 'js/components/Settings/SettingsSection';
import VirtualizedParameterTable from 'js/components/Parameters/VirtualizedParameterTable';
import ParametersControlSection from 'js/components/Parameters/ParametersControlSection';
import CalibrationSection from 'js/components/Calibration/CalibrationSection';
import Scratchpad from 'js/components/FlightNotes/Scratchpad';
import {initKeyBindings, setScope} from 'js/utils/KeyBindings';

import GlobalStore from 'js/stores/GlobalStore';

export default class GCS extends React.Component {
  /**
   * Hides all non-home tabs and sets up key bindings
   * @returns {undefined}
   */
  componentDidMount() {
    $('#settings').hide();
    $('#parameters').hide();
    $('#calibration').hide();
    $('#flightnotes').hide();
    initKeyBindings();
  }

  render() {
    return (
      <Provider store={GlobalStore} >
        <div className='root full-height'>  
          <NavbarSection />
            <div id='home' className='main-height'>
              <PlaneInfoSection />
              <WaypointContainer />
              <div className='main full-height'>
                <Slider />
                <MapSection />
              </div> 
          </div>
          <div id='settings'>
            <SettingsSection />
          </div>
          <div id='parameters'>
            <div className='row'>
              <VirtualizedParameterTable />
              <ParametersControlSection />
            </div>
          </div>
          <div id='calibration'>
            <CalibrationSection />
          </div>
          <div id='flightnotes'>
            <Scratchpad />
          </div>
        </div>
      </Provider>
    );
  }
}
