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
import { roundTo } from '../../../utils/math'

import styles from './ConfigForm.module.scss'

class ConfigForm extends Component {
  handleUpdateMs = (name, value) => {
    const { configurations, updateMsBsAeConnect } = this.props
    const data = {
      ms_temp: configurations.ms_temp,
      ms_rate_param: configurations.ms_rate_param,
    }

    if (value === '') data[name] = 0
    else data[name] = parseFloat(value)
    updateMsBsAeConnect('ms', data)
  }

  toggleMsAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_ms', value)

    if (value) {
      getMsBsAeConnect('ms')
    } else {
      updateMsBsAeConnect('ms', {
        ms_temp: configurations.ms_temp,
        ms_rate_param: configurations.ms_rate_param,
      })
    }
  }

  handleUpdateAe = (name, value) => {
    const { configurations, updateMsBsAeConnect } = this.props
    const data = {
      ae1_temp: configurations.ae1_temp,
      ae3_temp: configurations.ae3_temp,
    }

    if (value === '') data[name] = 0
    else data[name] = parseFloat(value)
    updateMsBsAeConnect('ae', data)
  }

  toggleAeAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_ae', value)

    if (value) {
      getMsBsAeConnect('ae')
    } else {
      updateMsBsAeConnect('ae', {
        ae1_temp: configurations.ae1_temp,
        ae3_temp: configurations.ae3_temp,
      })
    }
  }

  handleUpdateBs = (name, value) => {
    const { updateMsBsAeConnect } = this.props
    const data = { [name]: parseFloat(value) }

    if (value === '') data[name] = 0
    updateMsBsAeConnect('bs', data)
  }

  toggleBsAutoCalc = (value) => {
    const {
      updateMsBsAeConnect, getMsBsAeConnect, setAutoCalculateConnect, configurations,
    } = this.props
    setAutoCalculateConnect('auto_calculate_bs', value)

    if (value) {
      getMsBsAeConnect('bs')
    } else {
      updateMsBsAeConnect('bs', {
        bs_temp: configurations.bs_temp,
      })
    }
  }

  render() {
    const {
      configurations,
      updateConfigMethodConnect,
      updateGrainSizeConnect,
      updateConfigConnect,
      isAuthenticated,
    } = this.props
    const methodOptions = [
      { label: 'Li (98)', value: 'Li98' },
      { label: 'Kirkaldy (83)', value: 'Kirkaldy83' },
    ]

    return (
      <React.Fragment>
        <div className={styles.first}>
          <div className="input-col">
            <div className={styles.headerContainer}>
              <h6>CCT/TTT method</h6>
              <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
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
              isDisabled={!isAuthenticated}
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
                  onChange={val => updateGrainSizeConnect('astm', val)}
                  value={configurations.grain_size_ASTM}
                  length="short"
                  isDisabled={!isAuthenticated}
                />
              </div>
              <span> = </span>
              <div className="input-row">
                <span>Diameter</span>
                <TextFieldExtra
                  type="text"
                  name="grain_size_diameter"
                  onChange={val => updateGrainSizeConnect('dia', val)}
                  value={configurations.grain_size_diameter}
                  length="short"
                  suffix="μm"
                  isDisabled={!isAuthenticated}
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
                <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
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
                    value={roundTo(configurations.ae1_temp, 1)}
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ae || !isAuthenticated}
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
                    value={roundTo(configurations.ae3_temp, 1)}
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ae || !isAuthenticated}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_ae"
                onChange={val => this.toggleAeAutoCalc(val)}
                isChecked={configurations.auto_calculate_ae}
                label="Auto-calculate Ae"
                isDisabled={!isAuthenticated}
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
                    value={roundTo(configurations.bs_temp, 1)}
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_bs || !isAuthenticated}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_bs"
                onChange={val => this.toggleBsAutoCalc(val)}
                isChecked={configurations.auto_calculate_bs}
                label="Auto-calculate BS"
                isDisabled={!isAuthenticated}
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
                    value={roundTo(configurations.ms_temp, 1)}
                    length="short"
                    suffix="°C"
                    isDisabled={configurations.auto_calculate_ms || !isAuthenticated}
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
                    value={roundTo(configurations.ms_rate_param, 1)}
                    length="short"
                    isDisabled={configurations.auto_calculate_ms || !isAuthenticated}
                  />
                </div>
              </div>
              <Checkbox
                name="auto_calculate_ms"
                onChange={val => this.toggleMsAutoCalc(val)}
                isChecked={configurations.auto_calculate_ms}
                label="Auto-calculate MS"
                isDisabled={!isAuthenticated}
              />
            </div>
          </div>
        </div>
        <div className={styles.third}>
          <div className={styles.headerContainer}>
            <h5>Nucleation parameters</h5>
            <Tooltip className={{ tooltip: styles.infoTip, container: styles.infoTipContainer }} position="bottom">
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
                onChange={val => updateConfigConnect('nucleation_start', val)}
                value={configurations.nucleation_start}
                length="short"
                suffix="%"
                isDisabled={!isAuthenticated}
              />
            </div>
            <div className="input-row">
              <span>Finish</span>
              <TextFieldExtra
                type="text"
                name="nucleation_finish"
                onChange={val => updateConfigConnect('nucleation_finish', val)}
                value={configurations.nucleation_finish}
                length="short"
                suffix="%"
                isDisabled={!isAuthenticated}
              />
            </div>
          </div>
        </div>
      </React.Fragment>
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
  configurations: PropTypes.shape({
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
