import React from 'react';
import sinon from 'sinon';
import { mount } from 'enzyme';

import NavbarLinkItem from 'js/components/Navbar/NavbarLinkItem';

describe('NavbarLinkItem', function() {

  let onButtonClick, wrapper;

  beforeEach(function() {
    onButtonClick = sinon.spy();
    wrapper = mount(<NavbarLinkItem key='TEST' name='link' onClick={onButtonClick} />);
  });

  it('contains "a" tag and "li" tag', function() {
    expect(wrapper.find('li').length).toEqual(1);
    expect(wrapper.find('li').find('a').length).toEqual(1);
  });

  it('contains name', function() {
    expect(wrapper.text()).toEqual('link');
  });

  it('calls onClick when clicked', function() {
    wrapper.find('a').simulate('click');
    expect(onButtonClick.calledOnce).toEqual(true);
  });
});
