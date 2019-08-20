import React, { Component } from 'react'
import PropTypes from 'prop-types'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button from '../../elements/button'

import styles from './CompSidebar.module.scss'

class CompSidebar extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showSettings: true,
    }
  }

  render() {
    const {
      values,
      onChange,
      onSimulate,
      storeInit,
    } = this.props
    const { showSettings } = this.state

    return (
      <div className={styles.sidebar}>
        <header>
          <h4>Composition</h4>
          <Button
            appearance="text"
            onClick={() => this.setState(prevState => ({
              showSettings: !prevState.showSettings,
            }))}
            IconComponent={(props) => {
              if (showSettings) return <ChevronUpIcon {...props} />
              return <ChevronDownIcon {...props} />
            }}
          >
            {showSettings ? 'Collapse' : 'Expand'}
          </Button>
        </header>
        <div style={{ display: showSettings ? 'block' : 'none' }}>
          <CompForm
            values={values}
            onChange={onChange}
          />
        </div>
        <div className={styles.table}>
          <CompTable
            data={values}
            onChange={onChange}
          />
        </div>
        <Button
          onClick={onSimulate}
          length="long"
          className={styles.btn}
          isDisabled={!storeInit}
        >
          RUN
        </Button>
      </div>
    )
  }
}

CompSidebar.propTypes = {
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
  onSimulate: PropTypes.func.isRequired,
  storeInit: PropTypes.bool.isRequired,
}

export default CompSidebar
