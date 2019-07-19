import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
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
  const grainSizeOptions = [
    { label: 'ASTM', value: 'ASTM' },
    { label: 'diam', value: 'diam' },
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
          <TextField
            type="text"
            name="grain_size"
            onChange={val => onChange('grain_size', val)}
            value={values.grain_size}
            length="short"
          />
          <Select
            name="grain_size_type"
            placeholder="Size unit"
            options={grainSizeOptions}
            value={
              grainSizeOptions[grainSizeOptions.findIndex(o => o.value === values.grain_size_type)]
              || null
            }
            length="long"
            onChange={option => onChange('grain_size_type', option)}
            className={styles.select}
          />
        </div>
      </div>
      <div className={styles.second}>
        <div className={`${styles.configCol} ${styles.firstConfigCol}`}>
          <div className={styles.configGroup}>
            <h5>Transformation definitions</h5>
            <div className={`input-row ${styles.firstColLabel}`}>
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
            <div className={`input-row ${styles.firstColLabel}`}>
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
          <div className={styles.configGroup}>
            <h5>User cooling profile</h5>
            <div className={`input-row ${styles.firstColLabel}`}>
              <span>Start temperature</span>
              <TextFieldExtra
                type="text"
                name="start_temp"
                onChange={val => onChange('start_temp', val)}
                value={values.start_temp}
                length="short"
                suffix="°C"
              />
            </div>
            <div className={`input-row ${styles.firstColLabel}`}>
              <span>Cooling rate -CCT</span>
              <TextFieldExtra
                type="text"
                name="cct_cooling_rate"
                onChange={val => onChange('cct_cooling_rate', val)}
                value={values.cct_cooling_rate}
                length="short"
                suffix="°C/sec"
                className={styles.longPadInput}
              />
            </div>
          </div>
        </div>
        <div className={styles.configCol}>
          <div className={styles.configGroup}>
            <h5>Transformation temperature limits</h5>
            <h6>Austenite start/stop temperature</h6>
            <div className={styles.splitCol}>
              <div>
                <div className={`input-row ${styles.secondColLabel}`}>
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
                <div className={`input-row ${styles.secondColLabel}`}>
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
              <div>
                <Checkbox
                  name="auto_calculate_ae"
                  onChange={val => onChange('auto_calculate_ae', val)}
                  isChecked={values.auto_calculate_ae}
                  label="Austenite auto-calculate"
                />
              </div>
            </div>
            <h6>Martensite/Bainite start/stop temperature</h6>
            <div className={styles.splitCol}>
              <div>
                <div className={`input-row ${styles.secondColLabel}`}>
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
                <div className={`input-row ${styles.secondColLabel}`}>
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
              <div>
                <Checkbox
                  name="auto_calculate_ms_bs"
                  onChange={val => onChange('auto_calculate_ms_bs', val)}
                  isChecked={values.auto_calculate_ms_bs}
                  label="MS/BS auto-calculate"
                />
                <div className={`input-row ${styles.secondColSelect}`}>
                  <span>Method</span>
                  <Select
                    name="transformation_method"
                    placeholder="Method"
                    options={methodOptions}
                    value={
                      methodOptions[
                        methodOptions.findIndex(o => o.value === values.transformation_method)
                      ]
                      || null
                    }
                    length="long"
                    onChange={option => onChange('transformation_method', option)}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.configCol}>
          <div className={styles.configGroup}>
            <h5>Equilibrium phase</h5>
            <div className={styles.splitCol}>
              <div>
                <div className={`input-row ${styles.thirdColLabel}`}>
                  <span>Xfe</span>
                  <TextField
                    type="text"
                    name="xfe_value"
                    onChange={val => onChange('xfe_value', val)}
                    value={values.xfe_value}
                    length="short"
                  />
                </div>
                <div className={`input-row ${styles.thirdColLabel}`}>
                  <span>Cf</span>
                  <TextFieldExtra
                    type="text"
                    name="cf_value"
                    onChange={val => onChange('cf_value', val)}
                    value={values.cf_value}
                    length="short"
                    suffix="wt"
                  />
                </div>
                <div className={`input-row ${styles.thirdColLabel}`}>
                  <span>Ceut</span>
                  <TextFieldExtra
                    type="text"
                    name="ceut_value"
                    onChange={val => onChange('ceut_value', val)}
                    value={values.ceut_value}
                    length="short"
                    suffix="wt"
                  />
                </div>
              </div>
              <div>
                <Checkbox
                  name="auto_calculate_xfe"
                  onChange={val => onChange('auto_calculate_xfe', val)}
                  isChecked={values.auto_calculate_xfe}
                  label="Equilibrium phase auto-calculate"
                  className={styles.shortCheckbox}
                />
              </div>
            </div>
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
    grain_size_type: PropTypes.string.isRequired,
    grain_size: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]).isRequired,
    nucleation_start: PropTypes.number.isRequired,
    nucleation_finish: PropTypes.number.isRequired,
    auto_calculate_xfe: PropTypes.bool.isRequired,
    xfe_value: PropTypes.number.isRequired,
    cf_value: PropTypes.number.isRequired,
    ceut_value: PropTypes.number.isRequired,
    auto_calculate_ms_bs: PropTypes.bool.isRequired,
    transformation_method: PropTypes.string.isRequired,
    ms_temp: PropTypes.number.isRequired,
    ms_undercool: PropTypes.number.isRequired,
    bs_temp: PropTypes.number.isRequired,
    auto_calculate_ae: PropTypes.bool.isRequired,
    ae1_temp: PropTypes.number.isRequired,
    ae3_temp: PropTypes.number.isRequired,
    start_temp: PropTypes.number.isRequired,
    cct_cooling_rate: PropTypes.number.isRequired,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  
}

export default connect(null, mapDispatchToProps)(ConfigForm)
