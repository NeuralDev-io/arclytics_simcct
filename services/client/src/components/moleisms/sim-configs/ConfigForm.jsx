/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Configurations form for a simulation. All input elements in this form
 * are disabled until the user chooses an alloy composition form the
 * CompForm component.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import InfoIcon from 'react-feather/dist/icons/info'
import { connect } from 'react-redux'
import Tooltip from '../../elements/tooltip'
import Select from '../../elements/select'
import TextField, { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'
import {
  updateConfigMethod, updateGrainSize, updateMsBsAe, getMsBsAe, setAutoCalculate, updateConfig,
} from '../../../state/ducks/sim/actions'
import { validate, validateGroup } from '../../../utils/validator'
import { roundTo } from '../../../utils/math'
import { constraints } from './utils/constraints'
import { ASTM2Dia, dia2ASTM } from '../../../utils/grainSizeConverter'

import styles from './ConfigForm.module.scss'

class ConfigForm extends Component {
  handleUpdateGrainSize = (unit, value) => {
    const { updateGrainSizeConnect } = this.props

    // validate
    const err = validate(value, constraints.grainSize)
    if (err !== undefined) {
      if (unit === 'astm') updateGrainSizeConnect(value, '', { astm: err, dia: 'Grain size can\'t be empty' })
      else updateGrainSizeConnect('', value, { astm: 'Grain size can\'t be empty', dia: err })
    } else {
      // if value is valid, check if the converted value is valid
      let converted
      if (unit === 'astm') converted = ASTM2Dia(parseFloat(value))
      else converted = dia2ASTM(parseFloat(value))

      const convertedErr = validate(converted.toString(), constraints.grainSize)
      if (convertedErr !== undefined) {
        if (unit === 'astm') updateGrainSizeConnect(value, converted, { astm: '', dia: convertedErr })
        else updateGrainSizeConnect(converted, value, { astm: convertedErr, dia: '' })
      } else if (unit === 'astm') updateGrainSizeConnect(value, converted, {})
      else updateGrainSizeConnect(converted, value, {})
    }
  }

  handleUpdateMs = (name, value) => {
    const { configurations, updateMsBsAeConnect } = this.props
    const data = {
      ms_temp: configurations.ms_temp,
      ms_rate_param: configurations.ms_rate_param,
    }
    data[name] = value

    const err = validate(value, constraints.ms)
    if (err !== undefined) {
      updateMsBsAeConnect('ms', name, data, { [name]: err })
    } else updateMsBsAeConnect('ms', name, data, {})
  }

  toggleMsAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_ms', value)

    if (value) {
      // if autocalculate is turned on, get the data from backend
      getMsBsAeConnect('ms')
    } else {
      // if turn off, make an update request to the backend
      // with the current data
      updateMsBsAeConnect('ms', '', {
        ms_temp: roundTo(parseFloat(configurations.ms_temp), 1),
        ms_rate_param: roundTo(parseFloat(configurations.ms_rate_param), 3),
      }, {})
    }
  }

  handleUpdateAe = (name, value) => {
    const { configurations, updateMsBsAeConnect } = this.props
    const data = {
      ae1_temp: configurations.ae1_temp,
      ae3_temp: configurations.ae3_temp,
    }
    data[name] = value

    const err = validate(value, constraints.ae)
    if (err !== undefined) {
      updateMsBsAeConnect('ae', name, data, { [name]: err })
    } else updateMsBsAeConnect('ae', name, data, {})
  }

  toggleAeAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_ae', value)

    if (value) {
      // if autocalculate is turned on, get the data from backend
      getMsBsAeConnect('ae')
    } else {
      // if turn off, make an update request to the backend
      // with the current data
      updateMsBsAeConnect('ae', '', {
        ae1_temp: roundTo(parseFloat(configurations.ae1_temp), 1),
        ae3_temp: roundTo(parseFloat(configurations.ae3_temp), 1),
      }, {})
    }
  }

  handleUpdateBs = (name, value) => {
    const { updateMsBsAeConnect } = this.props
    const data = { [name]: value }

    const err = validate(value, constraints.bs)
    if (err !== undefined) {
      updateMsBsAeConnect('bs', name, data, { [name]: err })
    } else updateMsBsAeConnect('bs', name, data, {})
  }

  toggleBsAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_bs', value)

    if (value) {
      // if autocalculate is turned on, get the data from backend
      getMsBsAeConnect('bs')
    } else {
      // if turn off, make an update request to the backend
      // with the current data
      updateMsBsAeConnect('bs', '', {
        bs_temp: roundTo(parseFloat(configurations.bs_temp), 1),
      }, {})
    }
  }

  handleUpdateNucleationParams = (name, value) => {
    const { updateConfigConnect, configurations } = this.props
    const other = name === 'nucleation_start' ? 'nucleation_finish' : 'nucleation_start'
    const data = {
      nucleation_start: configurations.nucleation_start,
      nucleation_finish: configurations.nucleation_finish,
    }
    data[name] = value

    let err
    if (name === 'nucleation_start') {
      err = validate(value, constraints.nucleationStart)
    } else if (name === 'nucleation_finish') {
      err = validate(value, constraints.nucleationFinish)
    }

    if (err !== undefined) {
      updateConfigConnect(name, value, { [name]: err })
      updateConfigConnect(other, data[other], {})
    } else {
      err = validateGroup(data, constraints.nucleationParams)
      if (err !== undefined) {
        updateConfigConnect(name, value, { [name]: err })
        updateConfigConnect(other, data[other], { [other]: err })
      } else {
        updateConfigConnect(name, value, {})
        updateConfigConnect(other, data[other], {})
      }
    }
  }

  render() {
    const {
      configurations,
      updateConfigMethodConnect,
      isAuthenticated,
      isInitialised,
    } = this.props
    const methodOptions = [
      { label: 'Li (98)', value: 'Li98' },
      { label: 'Kirkaldy (83)', value: 'Kirkaldy83' },
    ]

    return (
      <>
        <div className={styles.first}>
          <div className="input-col">
            <div className={styles.headerContainer}>
              <h6>CCT/TTT method</h6>
              <Tooltip className={{ tooltip: `${styles.infoTip} ${styles.methodTooltip}`, container: styles.infoTipContainer }} position="right">
                <InfoIcon className={styles.infoIcon} />
                <p>
                  J.S.Krikaldy, et al., &quot;Prediction of microstructure and hardenability in
                  <br />
                  low-alloy steels&quot;, in Phase Transformations in ferrous alloys 1983,
                  <br />
                  p.125-148
                  <br />
                  <br />
                  M. V. Li, et.al. &quot;A Computational Model for the Prediction of Steel
                  <br />
                  Hardenability&quot;, Metallurgic and Materials Transactions, Vol29B, June
                  <br />
                  p.661-672 The method has been implemented EXACTLY as stated in the paper.
                </p>
              </Tooltip>
            </div>
            <Select
              name="method"
              placeholder="Method"
              options={methodOptions}
              value={
                methodOptions[methodOptions.findIndex(o => o.value === configurations.method)]
                || null
              }
              length="long"
              onChange={option => updateConfigMethodConnect(option.value)}
              isDisabled={!isAuthenticated || !isInitialised}
            />
          </div>
          <div className="input-col">
            <div className={styles.headerContainer}>
              <h6>Grain size</h6>
              <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
                <InfoIcon className={styles.infoIcon} />
                <p>
                  Plots a sigmoidal function distribution on a separate sheet.
                  <br />
                  This is for visualizing the various Sigmoidal distributions used:
                  <br />
                  <br />
                  S(X) - Li98(Ferrite, Pearlite, Bianite)
                  <br />
                  I(X) - Krikaldy (Ferrite Pearlite)
                  <br />
                  I&apos;(X) - Kirkaldy (Bainite)
                  <br />
                </p>
              </Tooltip>
            </div>
            <div className={styles.grainSize}>
              <div className="input-row">
                <span>ASTM</span>
                <TextField
                  type="text"
                  name="grain_size_ASTM"
                  onChange={val => this.handleUpdateGrainSize('astm', val)}
                  value={configurations.grain_size_ASTM}
                  length="short"
                  isDisabled={!isAuthenticated || !isInitialised}
                  error={configurations.error.astm}
                />
              </div>
              <span> = </span>
              <div className="input-row">
                <span>Diameter</span>
                <TextFieldExtra
                  type="text"
                  name="grain_size_diameter"
                  onChange={val => this.handleUpdateGrainSize('dia', val)}
                  value={configurations.grain_size_diameter}
                  length="short"
                  suffix="μm"
                  isDisabled={!isAuthenticated || !isInitialised}
                  error={configurations.error.dia}
                />
              </div>
            </div>
          </div>
        </div>
        <div className={styles.second}>
          <h5>Transformation limits</h5>
          <div className={styles.configRow}>
            <div>
              <div className={styles.headerContainer}>
                <h6>Ferrite/Pearlite</h6>
                <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="right">
                  <InfoIcon className={styles.infoIcon} />
                  <p>
                    Ae3 = temperature below austenite to ferrite transformation becomes
                    thermodynamically possible.
                  </p>
                </Tooltip>
              </div>
              <div className={styles.configGroup}>
                <div className="input-row">
                  <span>
                    A
                    <sub>e1</sub>
                  </span>
                  <TextFieldExtra
                    type="text"
                    name="ae1_temp"
                    onChange={val => this.handleUpdateAe('ae1_temp', val)}
                    value={
                      configurations.auto_calculate_ae
                        ? roundTo(parseFloat(configurations.ae1_temp), 1)
                        : configurations.ae1_temp
                    }
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ae || !isAuthenticated || !isInitialised}
                    error={configurations.error.ae1_temp}
                  />
                </div>
                <div className="input-row">
                  <span>
                    A
                    <sub>e3</sub>
                  </span>
                  <TextFieldExtra
                    type="text"
                    name="ae3_temp"
                    onChange={val => this.handleUpdateAe('ae3_temp', val)}
                    value={
                      configurations.auto_calculate_ae
                        ? roundTo(parseFloat(configurations.ae3_temp), 1)
                        : configurations.ae3_temp
                    }
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ae || !isAuthenticated || !isInitialised}
                    error={configurations.error.ae3_temp}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_ae"
                onChange={val => this.toggleAeAutoCalc(val)}
                isChecked={configurations.auto_calculate_ae}
                label="Auto-calculate Ae"
                isDisabled={!isAuthenticated || !isInitialised}
              />
            </div>
            <div>
              <div className={styles.headerContainer}>
                <h6>Bainite</h6>
                <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
                  <InfoIcon className={styles.infoIcon} />
                  <p>
                    Bainite transformation temperature (C)
                  </p>
                </Tooltip>
              </div>
              <div className={`${styles.configGroup} ${styles.bainite}`}>
                <div className="input-row">
                  <span>
                    B
                    <sub>s</sub>
                  </span>
                  <TextFieldExtra
                    type="text"
                    name="bs_temp"
                    onChange={val => this.handleUpdateBs('bs_temp', val)}
                    value={
                      configurations.auto_calculate_bs
                        ? roundTo(parseFloat(configurations.bs_temp), 1)
                        : configurations.bs_temp
                    }
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_bs || !isAuthenticated || !isInitialised}
                    error={configurations.error.bs_temp}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_bs"
                onChange={val => this.toggleBsAutoCalc(val)}
                isChecked={configurations.auto_calculate_bs}
                label="Auto-calculate BS"
                isDisabled={!isAuthenticated || !isInitialised}
              />
            </div>
            <div>
              <div className={styles.headerContainer}>
                <h6>Martensite</h6>
                <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
                  <InfoIcon className={styles.infoIcon} />
                  <p>
                    Martensite transformation temperature (C)
                    <br />
                    <br />
                    Martensite under cool temperature (C)
                  </p>
                </Tooltip>
              </div>
              <div className={styles.configGroup}>
                <div className="input-row">
                  <span>
                    M
                    <sub>s</sub>
                  </span>
                  <TextFieldExtra
                    type="text"
                    name="ms_temp"
                    onChange={val => this.handleUpdateMs('ms_temp', val)}
                    value={
                      configurations.auto_calculate_ms
                        ? roundTo(parseFloat(configurations.ms_temp), 1)
                        : configurations.ms_temp
                    }
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ms || !isAuthenticated || !isInitialised}
                    error={configurations.error.ms_temp}
                  />
                </div>
                <div className="input-row">
                  <span>
                    M
                    <sub>s</sub>
                    &nbsp;rate parameter
                  </span>
                  <TextField
                    type="text"
                    name="ms_rate_param"
                    onChange={val => this.handleUpdateMs('ms_rate_param', val)}
                    value={
                      configurations.auto_calculate_ms
                        ? roundTo(parseFloat(configurations.ms_rate_param), 3)
                        : configurations.ms_rate_param
                    }
                    length="short"
                    isDisabled={configurations.auto_calculate_ms || !isAuthenticated || !isInitialised}
                    error={configurations.error.ms_rate_param}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_ms"
                onChange={val => this.toggleMsAutoCalc(val)}
                isChecked={configurations.auto_calculate_ms}
                label="Auto-calculate MS"
                isDisabled={!isAuthenticated || !isInitialised}
              />
            </div>
          </div>
        </div>
        <div className={styles.third}>
          <div className={styles.headerContainer}>
            <h5>Nucleation parameters</h5>
            <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="right">
              <InfoIcon className={styles.infoIcon} />
              <p>
                Plots a sigmoidal function distribution on a separate sheet This is for
                visualizing the various Sigmoidal distributions used:
                <br />

                S(X) - Li98(Ferrite, Pearlite, Bianite)

                I(X) - Krikaldy (Ferrite Pearlite)

                I&apos;(X) - Kirkaldy (Bainite)
              </p>
            </Tooltip>
          </div>
          <div className={styles.configGroup}>
            <div className="input-row">
              <span>Start</span>
              <TextFieldExtra
                type="text"
                name="nucleation_start"
                onChange={val => this.handleUpdateNucleationParams('nucleation_start', val)}
                value={configurations.nucleation_start}
                length="short"
                suffix="%"
                isDisabled={!isAuthenticated || !isInitialised}
                error={configurations.error.nucleation_start}
              />
            </div>
            <div className="input-row">
              <span>Finish</span>
              <TextFieldExtra
                type="text"
                name="nucleation_finish"
                onChange={val => this.handleUpdateNucleationParams('nucleation_finish', val)}
                value={configurations.nucleation_finish}
                length="short"
                suffix="%"
                isDisabled={!isAuthenticated || !isInitialised}
                error={configurations.error.nucleation_finish}
              />
            </div>
          </div>
        </div>
      </>
    )
  }
}

const textFieldType = PropTypes.oneOfType([
  PropTypes.string,
  PropTypes.number,
])

ConfigForm.propTypes = {
  isAuthenticated: PropTypes.bool.isRequired,
  // props from connect()
  isInitialised: PropTypes.bool.isRequired,
  configurations: PropTypes.shape({
    error: PropTypes.shape({}),
    method: PropTypes.string,
    grain_size_ASTM: textFieldType,
    grain_size_diameter: textFieldType,
    nucleation_start: textFieldType,
    nucleation_finish: textFieldType,
    auto_calculate_bs: PropTypes.bool,
    auto_calculate_ms: PropTypes.bool,
    ms_temp: textFieldType,
    ms_rate_param: textFieldType,
    bs_temp: textFieldType,
    auto_calculate_ae: PropTypes.bool,
    ae1_temp: textFieldType,
    ae3_temp: textFieldType,
    start_temp: textFieldType,
    cct_cooling_rate: textFieldType,
  }).isRequired,
  updateConfigMethodConnect: PropTypes.func.isRequired,
  updateGrainSizeConnect: PropTypes.func.isRequired,
  updateMsBsAeConnect: PropTypes.func.isRequired,
  getMsBsAeConnect: PropTypes.func.isRequired,
  setAutoCalculateConnect: PropTypes.func.isRequired,
  updateConfigConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  configurations: state.sim.configurations,
  isInitialised: state.sim.isInitialised,
})

const mapDispatchToProps = {
  updateConfigMethodConnect: updateConfigMethod,
  updateGrainSizeConnect: updateGrainSize,
  updateMsBsAeConnect: updateMsBsAe,
  getMsBsAeConnect: getMsBsAe,
  setAutoCalculateConnect: setAutoCalculate,
  updateConfigConnect: updateConfig,
}

export default connect(mapStateToProps, mapDispatchToProps)(ConfigForm)
