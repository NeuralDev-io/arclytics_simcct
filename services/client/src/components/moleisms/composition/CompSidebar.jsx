import React, { Component } from 'react'
import PropTypes from 'prop-types'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button from '../../elements/button'

import styles from './CompSidebar.module.scss'

// eslint-disable-next-line
class CompSidebar extends Component {
  render() {
    const {
      values,
      onChange,
      onSimulate,
    } = this.props

    return (
      <div className={styles.sidebar}>
        <div>
          <h3>Composition</h3>
          <CompForm
            values={values}
            onChange={onChange}
          />
          <CompTable
            data={values.compositions}
          />
        </div>
        <Button
          onClick={onSimulate}
          length="long"
          className={styles.btn}
        >
          RUN
        </Button>
      </div>
    )
  }
}

CompSidebar.propTypes = {
  values: PropTypes.shape({
    alloy: PropTypes.string,
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
  onSimulate: PropTypes.func.isRequired,
}

export default CompSidebar
