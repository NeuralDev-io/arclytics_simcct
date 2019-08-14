import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Select from '../../elements/select'
import { TextFieldExtra } from '../../elements/textfield'
import { getGlobalAlloys, getUserAlloys } from '../../../state/ducks/alloys/actions'

import styles from './CompForm.module.scss'

class CompForm extends Component {
  componentDidMount = () => {
    const {
      globalAlloys,
      userAlloys,
      getGlobalAlloysConnect,
      getUserAlloysConnect,
    } = this.props
    if (!globalAlloys || globalAlloys.length === 0) {
      getGlobalAlloysConnect()
    }
    if (!userAlloys || userAlloys.length === 0) {
      getUserAlloysConnect()
    }
  }

  render() {
    const {
      globalAlloys,
      userAlloys,
      values,
      onChange,
    } = this.props

    const alloyOptions = [
      { label: 'Single', value: 'single' },
      { label: 'Both', value: 'both' },
      { label: 'Diluted mix', value: 'mix' },
    ]

    const globalOptions = globalAlloys.map(alloy => ({ label: alloy.name, value: alloy.name }))
    const userOptions = userAlloys.map(alloy => ({ label: alloy.name, value: alloy.name }))
    const compOptions = [
      {
        label: 'Global alloys',
        options: globalOptions,
      },
      {
        label: 'User alloys',
        options: userOptions,
      },
    ]

    return (
      <form className={styles.form}>
        <div className="input-row">
          <h6>Alloy option</h6>
          <Select
            name="alloyOption"
            placeholder="Choose alloy"
            options={alloyOptions}
            value={
              alloyOptions[alloyOptions.findIndex(o => o.value === values.alloyOption)]
              || null
            }
            length="long"
            onChange={val => onChange('alloyOption', val)}
          />
        </div>
        <div className="input-col">
          <h6>Alloy 1</h6>
          <Select
            name="parent"
            placeholder="Choose composition"
            options={compOptions}
            value={
              globalOptions[globalOptions.findIndex(c => c.value === values.parent.name)]
              || userOptions[userOptions.findIndex(c => c.value === values.parent.name)]
              || null
            }
            length="stretch"
            onChange={val => onChange('parent', val)}
            className={styles.select}
            isSearchable
          />
        </div>
        <div className="input-col">
          <h6 className={`${values.alloyOption === 'single' && 'text--disabled'}`}>Alloy 2</h6>
          <Select
            name="weld"
            placeholder="Choose composition"
            options={compOptions}
            value={
              globalOptions[globalOptions.findIndex(c => c.value === values.weld.name)]
              || userOptions[userOptions.findIndex(c => c.value === values.weld.name)]
              || null
            }
            length="stretch"
            onChange={val => onChange('weld', val)}
            className={styles.select}
            isDisabled={values.alloyOption === 'single'}
            isSearchable
          />
        </div>
        <div className="input-col">
          <h6 className={`${(values.alloyOption === 'single' || values.alloyOption === 'both') && 'text--disabled'}`}>Dilution</h6>
          <TextFieldExtra
            type="text"
            name="dilution"
            placeholder="Dilution"
            value={values.dilution}
            length="short"
            onChange={val => onChange('dilution', val)}
            suffix="%"
            isDisabled={values.alloyOption === 'single' || values.alloyOption === 'both'}
          />
        </div>
      </form>
    )
  }
}

CompForm.propTypes = {
  values: PropTypes.shape({
    alloyOption: PropTypes.string,
    parent: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    weld: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    mix: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    dilution: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  globalAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  userAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  getGlobalAlloysConnect: PropTypes.func.isRequired,
  getUserAlloysConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
  userAlloys: state.alloys.user,
})

const mapDispatchToProps = {
  getGlobalAlloysConnect: getGlobalAlloys,
  getUserAlloysConnect: getUserAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompForm)
