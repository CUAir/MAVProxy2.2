import React from 'react';
import { mount } from 'enzyme';

import { BUTTON } from 'js/constants/ButtonTypes';

import CalibrationControlSection from 'js/components/Calibration/CalibrationControlSection';

describe('CalibrationControlSection', function() {

  let wrapper;

  beforeEach(function() {
    wrapper = mount(<CalibrationControlSection />);
  });

  it('renders without error', function() {
  });

  it('renders all elements from store', function() {
    expect(wrapper.find('FullWidthElement').length).toEqual(7);
  });

  it('renders given controls correctly', function() {
    const controls = [
      {color: 'success', text: 'Button1', type: BUTTON, onClick: () => {}, key: 'BUTTON_1'},
      {color: 'unknown', text: 'Button2', type: BUTTON, onClick: () => {}, key: 'BUTTON_2'}
    ];
    wrapper.setState({controls: controls}, function() {
      expect(wrapper.find('FullWidthElement').length).toEqual(2);
      expect(wrapper.find('FullWidthElement').at(0).props().color).toEqual('success');
      expect(wrapper.find('FullWidthElement').at(0).props().text).toEqual('Button1');
      expect(wrapper.find('FullWidthElement').at(0).props().onClick).toBeInstanceOf(Function);
    });
  });

  it('unmounts without error', function() {
    wrapper.unmount();
  });
});
