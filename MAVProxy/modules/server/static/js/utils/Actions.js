// @flow

import type { PointType, ObstacleType, FlightType, TargetImgType,
              AirspeedType, AttitudeType, GpsType, WindType,
              LinkType, BatteryType, PowerboardType, ParamType } from 'js/utils/Objects';

type AddCalibrationLineAction = {type: 'ADD_CALIBRATION_LINE', line: string};
type ClearCalibrationAction = {type: 'CLEAR_CALIBRATION'};
export type CalibrationAction = AddCalibrationLineAction | ClearCalibrationAction;

type ReceiveFencePointsAction = {type: 'RECEIVE_FENCE_POINTS', points: PointType[]};
type ReceiveFencesEnabledAction = {type: 'RECEIVE_FENCES_ENABLED', enabled: boolean};
type SaveFencesAction = {type: 'SAVE_FENCES', points: PointType[]};
export type FenceAction = ReceiveFencePointsAction | ReceiveFencesEnabledAction | SaveFencesAction;

type ReceiveInteropAliveAction = {type: 'RECEIVE_INTEROP_ALIVE', alive: boolean};
type ReceiveInteropActiveAction = {type: 'RECEIVE_INTEROP_ACTIVE', active: boolean};
type ReceiveObstaclesAction = {type: 'RECEIVE_OBSTACLES', obstacles: {stationary_obstacles: ObstacleType[]}
};
type ReceiveOffAxisAction = {type: 'RECEIVE_OFF_AXIS', off_axis: PointType};
type ReceiveMissionWpDistsAction = {type: 'RECEIVE_MISSION_WP_DISTS', mission_wp_dists: number[]};
type ReceiveGimbalLocationAction = {type: 'GIMBAL_LOCATION', location: PointType};
type ReceiveOffaxistargetEnabledAction = {type: 'RECEIVE_OFFAXISTARGET_ENABLED', enabled: boolean};
type ReceiveGimbalStatusAction = {type: 'GIMBAL_STATUS', status: boolean};
export type InteropAction = ReceiveInteropAliveAction | ReceiveInteropActiveAction
  | ReceiveObstaclesAction | ReceiveOffAxisAction | ReceiveMissionWpDistsAction
  | ReceiveGimbalLocationAction | ReceiveOffaxistargetEnabledAction
  | ReceiveGimbalStatusAction;

type ReceiveSdaEnabledAction = {type: 'RECEIVE_SDA_ENABLED', enabled: boolean};
export type SdaAction = ReceiveSdaEnabledAction;

type ReceiveLocationsAction = {type: 'RECEIVE_LOCATIONS', locations: Object};
type UnitSwitchAction = {type: 'UNIT_SWITCH', value: boolean};
type ChangeHistoricalSliderAction = {type: 'CHANGE_HISTORICAL_SLIDER', value: boolean};
type ChangeFutureSliderAction = {type: 'CHANGE_FUTURE_SLIDER', value: boolean};
type ChangeSliderVisibleAction = {type: 'CHANGE_SLIDER_VISIBLE', value: boolean};
type ChangeSliderAction = {type: 'CHANGE_SLIDER', value: number};
type ChangeDateAction = {type: 'CHANGE_DATE', value: number};
type ChangeBatteryBeforeAction = {type: 'CHANGE_BATTERY_BEFORE', battery: string, value: number};
type ChangeBatteryAfterAction = {type: 'CHANGE_BATTERY_AFTER', battery: string, value: number};
type SaveFlightAction = {type: 'SAVE_FLIGHT', flight: FlightType};
type DownloadFlightcardAction = {type: 'DOWNLOAD_FLIGHTCARD'};
type ClearFlightsAction = {type: 'CLEAR_FLIGHTS'};
type ChangeWindAction = {type: 'CHANGE_WIND', wind: string, value: number};
type ChangeFlightnotesAction = {type: 'CHANGE_FLIGHTNOTES', flight_notes: string};
type ChangeAirframeAction = {type: 'CHANGE_AIRFRAME', airframe: string};
type ReceiveLocationAction = {type: 'RECEIVE_LOCATION', location: string};
type ReceiveScratchpadAction = {type: 'RECEIVE_SCRATCHPAD', scratchpad: string};
type ReceiveInteropUrlAction = {type: 'RECEIVE_INTEROP_URL', interopUrl: string};
type ReceiveObcUrlAction = {type: 'RECEIVE_OBC_URL', obcUrl: string};
type ReceiveInteropUsernameAction = {type: 'RECEIVE_INTEROP_USERNAME', interopUsername: string};
type ReceiveInteropPasswordAction = {type: 'RECEIVE_INTEROP_PASSWORD', interopPassword: string};
type ReceiveInteropMissionIDAction = {type: 'RECEIVE_INTEROP_MISSION_ID', interopMissionID: string};
type ReceiveDistributedUrlAction = {type: 'RECEIVE_DISTRIBUTED_URL', distributedUrl: string};
type ReceiveTokenAction = {type: 'RECEIVE_TOKEN', token: string};
type ReceiveScrollStartAction = {type: 'RECEIVE_SCROLL_START', scrollStart: number};
type ReceiveScrollEndAction = {type: 'RECEIVE_SCROLL_END', scrollEnd: number};
type ReceiveSdaModeAction = {type: 'RECEIVE_SDA_MODE', sdaMode: boolean};
export type SettingsAction = ReceiveLocationsAction | UnitSwitchAction 
  | ChangeHistoricalSliderAction | ChangeFutureSliderAction | ChangeSliderAction | ChangeDateAction
  | ChangeBatteryBeforeAction | ChangeBatteryAfterAction | SaveFlightAction
  | DownloadFlightcardAction | ClearFlightsAction | ChangeWindAction
  | ChangeFlightnotesAction | ChangeAirframeAction | ReceiveLocationAction
  | ReceiveScratchpadAction | ReceiveInteropUrlAction | ReceiveObcUrlAction
  | ReceiveInteropUsernameAction | ReceiveInteropPasswordAction | ReceiveInteropMissionIDAction
  | ReceiveDistributedUrlAction | ReceiveTokenAction | ReceiveScrollStartAction
  | ReceiveScrollEndAction | ReceiveSdaModeAction | ChangeSliderVisibleAction;

type ReceiveTargetImageAction = {type: 'RECEIVE_TARGET_IMAGE', targetImages: TargetImgType[]};
type ReceiveDistributedActiveAction = {type: 'RECEIVE_DISTRIBUTED_ACTIVE', active: boolean};
type ReceiveCoverageImageAction = {type: 'RECEIVE_COVERAGE_IMG', url: string, version: number, ext: string};
export type TargetImageAction = ReceiveTargetImageAction | ReceiveDistributedActiveAction
  | ReceiveCoverageImageAction;

type ReceiveAirspeedAction = {type: 'RECEIVE_AIRSPEED', airspeed: AirspeedType};
type ReceiveClimbRateAction = {type: 'RECEIVE_CLIMB_RATE', climb_rate: number};
type ReceiveAttitudeAction = {type: 'RECEIVE_ATTITUDE', attitude: AttitudeType};
type ReceiveGpsAction = {type: 'RECEIVE_GPS', gps: GpsType};
type ReceiveWindAction = {type: 'RECEIVE_WIND', wind: WindType};
type ReceiveGpsStatusAction = {type: 'RECEIVE_GPS_STATUS', gps_status: number};
type ReceiveSignalStrengthAction = {type: 'RECEIVE_SIGNAL_STRENGTH', signal_strength: number};
type ReceiveArmedAction = {type: 'RECEIVE_ARMED', armed: boolean};
type ReceivedSafetySwitchAction = {type: 'DOWNLOAD_FLIGHTCARD', safety_switch: boolean};
type ReceiveGpsLinkAction = {type: 'RECEIVE_GPS_LINK', gps_link: boolean};
type ReceivePlaneLinkAction = {type: 'RECEIVE_PLANE_LINK', plane_link: boolean};
type ReceiveLinkDetailsAction = {type: 'RECEIVE_LINK_DETAILS', links: LinkType[]};
type ReceiveBatteryAction = {type: 'RECEIVE_BATTERY', battery: BatteryType};
type ReceivePowerboardAction = {type: 'RECEIVE_POWERBOARD', powerboard: PowerboardType};
type ReceiveThrottleAction = {type: 'RECEIVE_THROTTLE', throttle: number};
type ReceiveCurrentModeAction = {type: 'RECEIVE_CURRENT_MODE', mode: string};
type ReceiveModeSwitchAction = {type: 'RECEIVE_MODE_SWITCH', mode_switch: string};
type ReceiveTimeToLandAction = {type: 'RECEIVE_TIME_TO_LAND', ttl: number};
type ReceiveMissionPercentAction = {type: 'RECEIVE_MISSION_PERCENT', mission_percent: number};
type ToggleShowTtlAction = {type: 'TOGGLE_SHOW_TTL'};
type LostConnectionAction = {type: 'LOST_CONNECTION'};
type GainedConnectionAction = {type: 'GAINED_CONNECTION'};
type StartFlightAction = {type: 'START_FLIGHT'};
type StopFlightAction = {type: 'STOP_FLIGHT'};
type UpdateFlightAction = {type: 'UPDATE_FLIGHT'};
export type StatusAction = ReceiveAirspeedAction | ReceiveClimbRateAction
  | ReceiveAttitudeAction | ReceiveGpsAction | ReceiveWindAction
  | ReceiveGpsStatusAction | ReceiveSignalStrengthAction | ReceiveArmedAction
  | ReceivedSafetySwitchAction | ReceiveGpsLinkAction | ReceivePlaneLinkAction
  | ReceiveLinkDetailsAction | ReceiveBatteryAction | ReceivePowerboardAction
  | ReceiveThrottleAction | ReceiveCurrentModeAction | ReceiveModeSwitchAction
  | ReceiveTimeToLandAction | ReceiveMissionPercentAction | ToggleShowTtlAction
  | LostConnectionAction | GainedConnectionAction | StartFlightAction
  | StopFlightAction | UpdateFlightAction;

type ReceiveSingleParameterAction = {type: 'RECEIVE_SINGLE_PARAMETER', name: string, value: string};
type ReceiveMultipleParametersAction = {type: 'RECEIVE_MULTIPLE_PARAMETERS', parameters: ParamType[]};
type ReceiveMaxParamCountAction = {type: 'RECEIVE_MAX_PARAM_COUNT', count: number};
type EditParameterAction = {type: 'EDIT_PARAMETER', name: string, value: string};
type SelectParameterAction = {type: 'SELECT_PARAMETER', name: string};
type ParameterLoadFromFileAction = {type: 'PARAMETER_LOAD_FROM_FILE', parameters: ParamType[]};
type ReceiveNoteAction = {type: 'RECEIVE_NOTE', note: string};
type ReceiveSearchFieldAction = {type: 'RECEIVE_SEARCH_FIELD', search_field: string};
type ReceiveModalOpenAction = {type: 'RECEIVE_MODAL_OPEN', open: boolean};
type ParameterSaveFromModal = {type: 'PARAMETER_SAVE_FROM_MODAL'};
type ResetParamCount = {type: 'RESET_PARAM_COUNT'};
export type ParametersAction = ReceiveSingleParameterAction
  | ReceiveMultipleParametersAction | ReceiveMaxParamCountAction
  | EditParameterAction | SelectParameterAction | ParameterLoadFromFileAction
  | ReceiveNoteAction | ReceiveSearchFieldAction | ReceiveModalOpenAction
  | ReceiveModalOpenAction | ParameterSaveFromModal | ResetParamCount;
