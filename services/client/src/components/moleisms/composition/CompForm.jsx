import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Select from '../../elements/select'
import { TextFieldExtra } from '../../elements/textfield'
import { getGlobalAlloys, getUserAlloys } from '../../../state/ducks/alloys/actions'
import { updateAlloyOption, initSession, updateDilution } from '../../../state/ducks/sim/actions'

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

  handleChangeAlloy = (name, option) => {
    const {
      simAlloys,
      initSessionConnect,
    } = this.props
    const alloy = this.findAlloy(option.value)

    initSessionConnect(simAlloys.alloyOption, name, alloy)
  }

  findAlloy = (id) => {
    const { globalAlloys, userAlloys } = this.props
    let idx = globalAlloys.findIndex(a => a._id === id)
    if (idx === -1) {
      idx = userAlloys.findIndex(a => a._id === id)
      return userAlloys[idx]
    }
    return globalAlloys[idx]
  }

  render() {
    const {
      globalAlloys,
      userAlloys,
      simAlloys,
      updateAlloyOptionConnect,
      updateDilutionConnect,
    } = this.props

    const alloyOptions = [
      { label: 'Single', value: 'single' },
      { label: 'Diluted mix', value: 'mix' },
    ]

    const globalOptions = globalAlloys.map(alloy => ({ label: alloy.name, value: alloy._id }))
    const userOptions = userAlloys.map(alloy => ({ label: alloy.name, value: alloy._id }))
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
              alloyOptions[alloyOptions.findIndex(o => o.value === simAlloys.alloyOption)]
              || null
            }
            length="long"
            onChange={val => updateAlloyOptionConnect(val.value)}
          />
        </div>
        <div className="input-col">
          <h6>Alloy 1</h6>
          <Select
            name="parent"
            placeholder="Choose composition"
            options={compOptions}
            value={
              globalOptions[globalOptions.findIndex(c => c.value === simAlloys.parent._id)]
              || userOptions[userOptions.findIndex(c => c.value === simAlloys.parent._id)]
              || null
            }
            length="stretch"
            onChange={val => this.handleChangeAlloy('parent', val)}
            className={styles.select}
            isSearchable
          />
        </div>
        <div className="input-col">
          <h6 className={`${simAlloys.alloyOption === 'single' && 'text--disabled'}`}>Alloy 2</h6>
          <Select
            name="weld"
            placeholder="Choose composition"
            options={compOptions}
            value={
              globalOptions[globalOptions.findIndex(c => c.value === simAlloys.weld._id)]
              || userOptions[userOptions.findIndex(c => c.value === simAlloys.weld._id)]
              || null
            }
            length="stretch"
            onChange={val => this.handleChangeAlloy('weld', val)}
            className={styles.select}
            isDisabled={simAlloys.alloyOption === 'single'}
            isSearchable
          />
        </div>
        <div className="input-col">
          <h6 className={`${simAlloys.alloyOption === 'single' && 'text--disabled'}`}>Dilution</h6>
          <TextFieldExtra
            type="text"
            name="dilution"
            placeholder="Dilution"
            value={simAlloys.dilution}
            length="short"
            onChange={val => updateDilutionConnect(val)}
            suffix="%"
            isDisabled={simAlloys.alloyOption === 'single'}
          />
        </div>
      </form>
    )
  }
}

CompForm.propTypes = {
  // props from connect()
  simAlloys: PropTypes.shape({
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
    mix: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
    dilution: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  }).isRequired,
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
  updateAlloyOptionConnect: PropTypes.func.isRequired,
  initSessionConnect: PropTypes.func.isRequired,
  updateDilutionConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
  userAlloys: state.alloys.user,
  simAlloys: state.sim.alloys,
})

const mapDispatchToProps = {
  getGlobalAlloysConnect: getGlobalAlloys,
  getUserAlloysConnect: getUserAlloys,
  updateAlloyOptionConnect: updateAlloyOption,
  initSessionConnect: initSession,
  updateDilutionConnect: updateDilution,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompForm)
