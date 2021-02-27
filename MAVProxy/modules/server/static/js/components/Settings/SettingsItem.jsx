// @flow

import React from 'react';

import { CHECKBOX, TEXT, DROPDOWN, FILE_INPUT, BUTTON, CRITICAL_BUTTON,
         DATETIME } from 'js/constants/ButtonTypes';

import SettingsCheckbox from 'js/components/Settings/SettingsCheckbox';
import SettingsText from 'js/components/Settings/SettingsText';
import SettingsDropdown from 'js/components/Settings/SettingsDropdown';
import SettingsFileInput from 'js/components/Settings/SettingsFileInput';
import SettingsButton from 'js/components/Settings/SettingsButton';
import SettingsCriticalButton from 'js/components/Settings/SettingsCriticalButton';
import SettingsDateTime from 'js/components/Settings/SettingsDateTime';

export default function SettingsItem(props: Object) {
  switch (props.type) {
  case CHECKBOX:
    return <SettingsCheckbox {...props} />;
  case TEXT:
    return <SettingsText {...props} />;
  case DROPDOWN:
    return <SettingsDropdown {...props} />;
  case FILE_INPUT:
    return <SettingsFileInput {...props} />;
  case BUTTON:
    return <SettingsButton {...props} />;
  case CRITICAL_BUTTON:
    return <SettingsCriticalButton {...props} />;
  case DATETIME:
    return <SettingsDateTime {...props} />;
  default:
    return null;
  }
}
