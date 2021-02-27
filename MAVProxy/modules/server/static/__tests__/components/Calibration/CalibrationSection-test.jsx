import React from 'react';
import { mount } from 'enzyme';

import CalibrationSection from 'js/components/Calibration/CalibrationSection';

describe('CalibrationControlSection', function() {

  const lines = ['This is a', 'And this is b'];

  let wrapper;

  beforeEach(function() {
    wrapper = mount(<CalibrationSection />);
  });

  it('renders without error', function() {
  });

  it('contains title', function() {
    expect(wrapper.find('h1').length).toEqual(1);
  });

  it('doesn\'t contain lines if empty', function() {
    expect(wrapper.find('p').length).toEqual(0);
  });

  it('contains lines if not empty', function() {
    wrapper.setState({lines: lines}, function() {
      expect(wrapper.find('p').length).toEqual(2);
      expect(wrapper.find('p').at(0).text()).toEqual(lines[0]);
      expect(wrapper.find('p').at(1).text()).toEqual(lines[1]);
    });
  });

  it('unmounts without error', function() {
    wrapper.unmount();
  });
});
