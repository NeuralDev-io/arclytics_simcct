/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Vertical slider component. A wrapper around the
 * react-compound-slider component to add extra styling
 * and custom properties for Arclytics SimCCT.
 *
 * For props reference, refer to the documentation at
 * https://sghall.github.io/react-compound-slider/#/
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import Slider, {
  Rail, Handles, Tracks, Ticks,
} from 'react-compound-slider'
import {
  SliderRail, Handle, Track, Tick,
} from './Components'

const sliderStyle = {
  position: 'relative',
  height: '22rem',
  marginLeft: '45%',
  touchAction: 'none',
}

const VerticalSlider = ({
  isDisabled,
  domain,
  step,
  values,
  tickCount,
  ...others
}) => (
  <div style={{ height: '100%', width: '100%' }}>
    <Slider
      vertical
      mode={2}
      rootStyle={sliderStyle}
      domain={domain}
      step={step}
      values={values}
      {...others}
    >
      <Rail>
        {({ getRailProps }) => <SliderRail getRailProps={isDisabled ? () => {} : getRailProps} />}
      </Rail>
      <Handles>
        {({ handles, getHandleProps }) => (
          <div className="slider-handles">
            {handles.map(handle => (
              <Handle
                key={handle.id}
                handle={handle}
                domain={domain}
                getHandleProps={isDisabled ? () => {} : getHandleProps}
              />
            ))}
          </div>
        )}
      </Handles>
      <Tracks left={false}>
        {({ tracks, getTrackProps }) => (
          <div className="slider-tracks">
            {tracks.map(({ id, source, target }) => (
              <Track
                key={id}
                source={source}
                target={target}
                getTrackProps={isDisabled ? () => {} : getTrackProps}
              />
            ))}
          </div>
        )}
      </Tracks>
      <Ticks count={tickCount}>
        {({ ticks }) => (
          <div className="slider-ticks">
            {ticks.map(tick => (
              <Tick key={tick.id} tick={tick} />
            ))}
          </div>
        )}
      </Ticks>
    </Slider>
  </div>
)

VerticalSlider.propTypes = {
  isDisabled: PropTypes.bool,
  domain: PropTypes.arrayOf(PropTypes.number).isRequired,
  step: PropTypes.number.isRequired,
  values: PropTypes.arrayOf(PropTypes.number).isRequired,
  tickCount: PropTypes.number,
}

VerticalSlider.defaultProps = {
  tickCount: -1,
  isDisabled: false,
}

export default VerticalSlider
