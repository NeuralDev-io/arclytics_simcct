import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Select from '../../elements/select'
import { getAlloys } from '../../../state/ducks/alloys/actions'

import styles from './CompForm.module.scss'

class CompForm extends Component {
  componentDidMount = () => {
    const { alloys, getAlloys } = this.props // eslint-disable-line
    if (!alloys || alloys.length === 0) {
      getAlloys()
    }
  }

  render() {
    const {
      alloys,
      values,
      onChange,
    } = this.props

    const alloyOptions = [
      { label: 'Alloy 1', value: 'parent' },
      { label: 'Alloy 2', value: 'weld' },
      { label: 'Diluted mix', value: 'mix' },
    ]

    const compOptions = alloys.map(alloy => ({ label: alloy.name, value: alloy.name }))

    return (
      <form className={styles.form}>
        <div className={styles.selectInline}>
          <h6>Select alloy</h6>
          <Select
            name="alloy"
            placeholder="Choose alloy"
            options={alloyOptions}
            value={
              alloyOptions[alloyOptions.findIndex(o => o.value === values.alloy)]
              || null
            }
            length="long"
            onChange={val => onChange('alloy', val)}
            className={styles.select}
          />
        </div>
        <h6 className={styles.heading}>Alloy 1</h6>
        <Select
          name="alloyComp"
          placeholder="Choose composition"
          options={compOptions}
          value={
            compOptions[compOptions.findIndex(c => c.value === values.composition)]
            || null
          }
          length="stretch"
          onChange={val => onChange('composition', val)}
          className={styles.select}
        />
      </form>
    )
  }
}

CompForm.propTypes = {
  values: PropTypes.shape({
    alloy: PropTypes.string,
    composition: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  alloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  getAlloys: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  alloys: state.alloys.list,
})

const mapDispatchToProps = {
  getAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompForm)
