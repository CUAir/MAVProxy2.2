import React from 'react';
import { mount } from 'enzyme';

import Scratchpad from 'js/components/FlightNotes/Scratchpad';

describe('Scratchpad', function() {

  let wrapper;

  beforeEach(function() {
    wrapper = mount(<Scratchpad />);
  });

  it('renders without error', function() {
  });

  it('renders textarea', function() {
    expect(wrapper.find('textarea').length).toEqual(1);
  });

  it('unmounts without error', function() {
    wrapper.unmount();
  });
});
