// @flow

import React from 'react';

import { BUTTON, FILE_INPUT, TEXT_INPUT } from 'js/constants/ButtonTypes';

import FullWidthButton from 'js/components/General/FullWidthButton';
import FullWidthFileInput from 'js/components/General/FullWidthFileInput';
import FullWidthTextInput from 'js/components/General/FullWidthTextInput';

export default function FullWidthElement(props: Object) {
  switch (props.type) {
  case BUTTON:
    return <FullWidthButton {...props} key={props.id} />;
  case FILE_INPUT:
    return <FullWidthFileInput {...props} />;
  case TEXT_INPUT:
    return <FullWidthTextInput {...props} />;
  default:
    return null;
  }
}
