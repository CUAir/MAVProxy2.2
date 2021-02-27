// 

import React from 'react';
import autobind from 'autobind-decorator';
import { connect } from 'react-redux';

import { changeSlider } from 'js/actions/SettingsActionCreator';
import { getConfigValue, configNames } from 'js/utils/ConfigData';
import { dateToString, decround } from 'js/utils/ComponentUtils';
import { getPlanePredictions } from 'js/utils/ReceiveApi';
import { updatePlanePredictionMarker } from 'js/utils/MapUtils'
import GlobalStore from 'js/stores/GlobalStore';
import { latitude } from 'geolib';

const playStyle = {marginRight: '10px'};
const REPLAY_SPEEDS = [{text: "1x", speed: 1000/1.}, 
                       {text: "2x", speed: 1000/2.}, 
                       {text: "8x", speed: 1000/8.}]

function mapStateToProps({ settings: { historical_slider, sdaMode, scrollStart, scrollEnd, slider_visible } }) {
  const milliseconds = scrollEnd - scrollStart;
  const seconds = historical_slider ? decround(milliseconds/1000, 0) : 20*60;
  return {
    historical: historical_slider,
    seconds, slider_visible,
    future: sdaMode,
    offset: scrollStart
  };
}

function Handle({ offset, value }, seconds, historical) {
  const style = Object.assign({}, {left: `${offset}%`}, handleStyle);
  const diff = 1000 * (seconds - value);
  const dateAtValue = !historical ? new Date(new Date() - diff) : new Date(parseFloat(getConfigValue(configNames.SCROLL_END)) - diff);
  const string = value === seconds && !historical ? 'Now' : dateToString(dateAtValue);
  return <div style={style}>{string}</div>;
}

function secondsToStrGen(offset: Date) {
  // returns a function that converts from number of seconds to a time string 
  return (value) => {
    return dateToString(new Date(offset.getTime() + value * 1000));
  }
}

class Slider extends React.Component {

  constructor(props) {
    super(props);
    this.state = {play: false, 
      value: props.future ? 0 : 20*60, 
      time_at_reset: (new Date()).getTime()/1000,
      replay_speed_selector: 0
    };
  }

  _interval = 0;

  @autobind
  _playPause() {
    const speed = REPLAY_SPEEDS[this.state.replay_speed_selector].speed;
    if (this.state.play) clearInterval(this._intervalCurrent); // person clicked pause
    else if (!this.state.play) this._intervalCurrent = setInterval(this._onTick, speed);
    this.setState({play: !this.state.play});
  }

  @autobind
  _toggleSpeed() {
    this.setState({replay_speed_selector: (this.state.replay_speed_selector + 1) % REPLAY_SPEEDS.length});
    const speed = REPLAY_SPEEDS[this.state.replay_speed_selector].speed;
    if (this.state.play) {
      clearInterval(this._intervalCurrent);
      this._intervalCurrent = setInterval(this._onTick, speed);
    }
  }

  @autobind
  _onTick() {
    const { future, historical } = this.props
    if (future) {
      this._futureOnChange(this.state.value + 1)
    } else if (historical) {
      this.setState({value: this.state.value + 1});
      changeSlider(this.state.value + 1);
    }

  }

  @autobind
  _reset() {
    this.setState({time_at_reset: (new Date()).getTime()/1000, value: 0.0});
    const { sda } = GlobalStore.getState();
    getPlanePredictions();
  }

  _futureOnChange(value) {
    this.setState({value});
    updatePlanePredictionMarker(this.state.time_at_reset, value);
  }

  render() {
    const icon = this.state.play ? 'pause' : 'play';
    const { seconds, future, value, slider_visible, offset } = this.props;
    if (!slider_visible) {
      // not enabled in settings, so no need to show.
      return <div />;
    } else if (future) {
      return (
        <div className="row" style={{paddingTop: '10px', marginBottom: '0px'}}>
          <div className="col s1" style={{paddingTop: '10px'}}>
            <button style={playStyle} onClick={this._reset} className="btn btn-default">
              <span>Reset</span>
            </button>
          </div>
        <div className="col s1" style={{paddingTop: '10px'}}>
            <button style={playStyle} onClick={this._playPause} className="btn btn-default">
              <span className={`fa fa-${icon}`}></span>
            </button>
          </div>
          <div className="col s10">
            <p className="range-field">
              <input type="range" onMouseUp={v => this._futureOnChange(parseFloat(v.target.value))}
                min={0} max={600} value={this.state.value}
                onChange={v => this._futureOnChange(parseFloat(v.target.value))} />
            </p>
          </div>
        </div>
      );
    } else {
        var toStr = secondsToStrGen(new Date(offset));
        return (
          <div className="row" style={{paddingTop: '10px', marginBottom: '0px'}}>
            <div className="col s10">
              <p className="range-field">
                <input 
                  type="range" name="rangeslider" onMouseUp={v => changeSlider(parseFloat(v.target.value))} 
                    min={0} max={seconds} value={(this.state.value)}
                  onChange={v => this.setState({value: parseFloat(v.target.value)})} 
                  style={{width: "90%"}} />
                  <span className="slider-label">{toStr(this.state.value)}</span>
              </p>
            </div>
            <div className="col s2" style={{paddingTop: '10px'}}>
              <button style={playStyle} onClick={this._playPause} className="btn btn-default">
                <span className={`fa fa-${icon}`}></span>
              </button>
              <button style={playStyle} onClick={this._toggleSpeed} className="btn btn-default">
                <span>{REPLAY_SPEEDS[this.state.replay_speed_selector].text}</span>
              </button>
            </div>
          </div>
        );
    }
  }
}

export default connect(mapStateToProps)(Slider);
