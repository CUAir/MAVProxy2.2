import React from 'react';
import { mount } from 'enzyme';

import NavbarStatusItem from 'js/components/Navbar/NavbarStatusItem';

describe('NavbarStatusItem', function() {

  let wrapper;

  function buildWrapper(status) {
    return mount(<NavbarStatusItem name='item-name' id='item-id' status={status} />);
  }

  it('displays text correctly', function() {
    wrapper = buildWrapper(true);
    expect(wrapper.find('a').at(0).text()).toEqual('item-name');
  });

  it('displays success status correctly', function() {
    wrapper = buildWrapper(true);
    expect(wrapper.find('li.btn-success').length).toEqual(1);
    expect(wrapper.find('li.btn-danger').length).toEqual(0);
  });

  it('displays fail status correctly', function() {
    wrapper = buildWrapper(false);
    expect(wrapper.find('li.btn-success').length).toEqual(0);
    expect(wrapper.find('li.btn-danger').length).toEqual(1);
  });
});
