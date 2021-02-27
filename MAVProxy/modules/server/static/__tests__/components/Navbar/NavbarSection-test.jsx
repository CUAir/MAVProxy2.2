import React from 'react';
import { mount } from 'enzyme';

import NavbarSection from 'js/components/Navbar/NavbarSection';

describe('NavbarSection', function() {

  let wrapper;

  beforeEach(function() {
    wrapper = mount(<NavbarSection />);
  });

  it('renders without error', function() {
  });

  it('contains navbar links', function() {
    expect(wrapper.find('#navbar-links').find('NavbarLinkItem').length).toEqual(6);
  });

  it('contains planeStatus items', function() {
    expect(wrapper.find('#planeStatus').find('NavbarStatusItem').length).toEqual(7);
  });

  it('contains logo', function() {
    expect(wrapper.find('#brand-button').find('img').length).toEqual(1);
  });

  it('unmounts without error', function() {
    wrapper.unmount();
  });
});
