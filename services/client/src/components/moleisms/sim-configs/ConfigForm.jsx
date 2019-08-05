import React from 'react'
import PropTypes from 'prop-types'
import Select from '../../elements/select'
import TextField, { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'

import styles from './ConfigForm.module.scss'

const ConfigForm = (props) => {
  const { values, onChange } = props
  const methodOptions = [
    { label: 'Li (98)', value: 'Li98' },
    { label: 'Kirkaldy (83)', value: 'Kirkaldy83' },
  ]

  return (
    <React.Fragment>
      <div className={styles.first}>
        <div className="input-row">
          <h6>CCT/TTT method</h6>
          <Select
            name="method"
            placeholder="Method"
            options={methodOptions}
            value={
              methodOptions[methodOptions.findIndex(o => o.value === values.method)]
              || null
            }
            length="long"
            onChange={option => onChange('method', option)}
          />
        </div>
        <div className="input-row">
          <h6>Grain size</h6>
          <div className="input-row">
            <div className="input-row">
              <span>ASTM</span>
              <TextField
                type="text"
                name="grain_size_ASTM"
                onChange={val => onChange('grain_size_ASTM', val)}
                value={values.grain_size_ASTM}
                length="short"
              />
            </div>
            <div className="input-row">
              <span>Diameter</span>
              <TextFieldExtra
                type="text"
                name="grain_size_diameter"
                onChange={val => onChange('grain_size_diameter', val)}
                value={values.grain_size_diameter}
                length="short"
                suffix="μ"
              />
            </div>
          </div>
        </div>
      </div>
      <div className={styles.second}>
        <h5>Transformation temperature</h5>
        <div className={styles.configRow}>
          <div>
            <h6>Austenite start/stop</h6>
            <div className={styles.configGroup}>
              <div className="input-row">
                <span>Ae1</span>
                <TextFieldExtra
                  type="text"
                  name="ae1_temp"
                  onChange={val => onChange('ae1_temp', val)}
                  value={values.ae1_temp}
                  length="short"
                  suffix="°C"
                />
              </div>
              <div className="input-row">
                <span>Ae3</span>
                <TextFieldExtra
                  type="text"
                  name="ae3_temp"
                  onChange={val => onChange('ae3_temp', val)}
                  value={values.ae3_temp}
                  length="short"
                  suffix="°C"
                />
              </div>
            </div>
            <Checkbox
              name="auto_calculate_ae"
              onChange={val => onChange('auto_calculate_ae', val)}
              isChecked={values.auto_calculate_ae}
              label="Auto-calculate Austenite"
            />
          </div>
          <div>
            <h6>Bainite start/stop</h6>
            <div className={styles.configGroup}>
              <div className="input-row">
                <span>BS</span>
                <TextFieldExtra
                  type="text"
                  name="bs_temp"
                  onChange={val => onChange('bs_temp', val)}
                  value={values.bs_temp}
                  length="short"
                  suffix="°C"
                />
              </div>
            </div>
            <Checkbox
              name="auto_calculate_bs"
              onChange={val => onChange('auto_calculate_bs', val)}
              isChecked={values.auto_calculate_bs}
              label="Auto-calculate BS"
            />
          </div>
          <div>
            <h6>Martensite start/stop</h6>
            <div className={styles.configGroup}>
              <div className="input-row">
                <span>MS</span>
                <TextFieldExtra
                  type="text"
                  name="ms_temp"
                  onChange={val => onChange('ms_temp', val)}
                  value={values.ms_temp}
                  length="short"
                  suffix="°C"
                />
              </div>
              <div className="input-row">
                <span>MS rate parameter</span>
                <TextField
                  type="text"
                  name="ms_rate_param"
                  onChange={val => onChange('ms_rate_param', val)}
                  value={values.ms_rate_param}
                  length="short"
                />
              </div>
            </div>
            <Checkbox
              name="auto_calculate_ms"
              onChange={val => onChange('auto_calculate_ms', val)}
              isChecked={values.auto_calculate_ms}
              label="Auto-calculate MS"
            />
          </div>
        </div>
      </div>
      <div className={styles.third}>
        <h5>Set up</h5>
        <div className={styles.configGroup}>
          <div className="input-row">
            <span>Nucleation start</span>
            <TextFieldExtra
              type="text"
              name="nucleation_start"
              onChange={val => onChange('nucleation_start', val)}
              value={values.nucleation_start}
              length="short"
              suffix="%"
            />
          </div>
          <div className="input-row">
            <span>Nucleation finish</span>
            <TextFieldExtra
              type="text"
              name="nucleation_finish"
              onChange={val => onChange('nucleation_finish', val)}
              value={values.nucleation_finish}
              length="short"
              suffix="%"
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  )
}

ConfigForm.propTypes = {
  values: PropTypes.shape({
    method: PropTypes.string.isRequired,
    alloy: PropTypes.string.isRequired,
    grain_size_ASTM: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]).isRequired,
    grain_size_diameter: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]).isRequired,
    nucleation_start: PropTypes.number.isRequired,
    nucleation_finish: PropTypes.number.isRequired,
    auto_calculate_bs: PropTypes.bool.isRequired,
    auto_calculate_ms: PropTypes.bool.isRequired,
    ms_temp: PropTypes.number.isRequired,
    ms_rate_param: PropTypes.number.isRequired,
    bs_temp: PropTypes.number.isRequired,
    auto_calculate_ae: PropTypes.bool.isRequired,
    ae1_temp: PropTypes.number.isRequired,
    ae3_temp: PropTypes.number.isRequired,
    start_temp: PropTypes.number.isRequired,
    cct_cooling_rate: PropTypes.number.isRequired,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
}

export default ConfigForm
