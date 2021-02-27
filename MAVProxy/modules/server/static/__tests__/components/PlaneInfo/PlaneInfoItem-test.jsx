import React from 'react';
import { mount } from 'enzyme';

import PlaneInfoItem from 'js/components/PlaneInfo/PlaneInfoItem';

describe('PlaneInfoItem', function() {

  let wrapper;

  function buildWrapper(value) {
    return mount(<table><tbody><PlaneInfoItem name='plane-name' id='item-id' value={value} unit='info-units' /></tbody></table>);
  }

  it('displays text correctly', function() {
    wrapper = buildWrapper(50);
    expect(wrapper.text().includes('plane-name')).toEqual(true);
    expect(wrapper.text().includes('50')).toEqual(true);
    expect(wrapper.text().includes('info-units')).toEqual(true);
    expect(wrapper.find('#item-id').length).toEqual(1);
  });
});
