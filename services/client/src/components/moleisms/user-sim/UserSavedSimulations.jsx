/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User saved simulations.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
/* eslint-disable react/jsx-props-no-spreading */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye } from '@fortawesome/pro-light-svg-icons/faEye'
import { faUpload } from '@fortawesome/pro-light-svg-icons/faUpload'
import { faTrashAlt } from '@fortawesome/pro-light-svg-icons/faTrashAlt'
import { faTimes } from '@fortawesome/pro-light-svg-icons/faTimes'
import Button, { IconButton } from '../../elements/button'
import Table from '../../elements/table'
import { getColor } from '../../../utils/theming'
import { getSavedSimulations } from '../../../state/ducks/self/actions'
import { loadSimFromAccount } from '../../../state/ducks/sim/actions'

import styles from './UserSavedSimulations.module.scss'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'

class UserSavedSimulations extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showSideView: false,
      currentSim: {},
    }
  }

  componentDidMount = () => {
    const { data = [], dataFetched = false, getSavedSimulationsConnect } = this.props
    if (data.length === 0 || !dataFetched) getSavedSimulationsConnect()
  }

  handleLoadSim = (sim) => {
    const { loadSimFromAccountConnect, redirect } = this.props
    loadSimFromAccountConnect(sim)
    redirect({
      pathname: '/',
      state: { loadFromAccount: true },
    })
  }

  handleViewSim = (sim) => {
    // eslint-disable-next-line no-underscore-dangle
    this.setState({ showSideView: true, currentSim: { _id: sim._id } })
    setTimeout(() => {
      this.setState({
        // showSideView: true,
        currentSim: sim,
      })
    }, 500)
  }

  handleCloseSideView = () => {
    this.setState({
      showSideView: false,
      currentSim: {},
    })
  }

  render() {
    const { showSideView, currentSim: { _id, ...currentSimContent } } = this.state
    let { data = [] } = this.props
    const { dataFetched, dataLoading } = this.props
    if (!dataFetched) data = []

    const columns = [
      {
        Header: 'Created',
        accessor: 'created',
        Cell: ({ value }) => (<span>{dangerouslyGetDateTimeString(value)}</span>),
        maxWidth: 180,
      },
      {
        Header: 'Alloy used',
        accessor: d => d.alloy_store.alloys.parent.name,
        id: 'alloy_name',
        // Cell: ({ value }) => (value !== undefined ? value.alloy_store.alloys.parent.name : ''),
        filterable: false,
        maxWidth: 180,
      },
      {
        Header: 'Method',
        accessor: d => d.configurations.method,
        id: 'method',
        filterable: false,
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
              onClick={() => this.handleLoadSim(original)}
              length="short"
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faUpload} {...props} />}
            >
              Load
            </Button>
            <Button
              onClick={() => this.handleViewSim(original)}
              length="short"
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faEye} {...props} />}
            >
              View
            </Button>
          </div>
        ),
        width: 180,
      },
    ]

    return (
      <>
        <div className={`${styles.mainview} ${showSideView ? styles.shrink : ''}`}>
          <h3>Saved simulations</h3>
          <Table
            className="-highlight"
            data={data}
            columns={columns}
            loading={dataLoading}
            pageSize={data.length > 10 ? 10 : data.length}
            showPageSizeOptions={false}
            showPagination={data.length !== 0}
            resizable={false}
            condensed
          />
        </div>
        <div className={`${styles.sideview} ${showSideView ? styles.show : ''}`}>
          <header className={styles.sideHeader}>
            <h5>
              Sim ID:
              {' '}
              {_id}
            </h5>
            <IconButton
              onClick={this.handleCloseSideView}
              Icon={props => <FontAwesomeIcon icon={faTimes} color={getColor('--n500')} {...props} />}
              className={styles.closeButton}
            />
          </header>
          <pre className="text--code">
            {JSON.stringify(currentSimContent, null, 2)}
          </pre>
          <div className={styles.sideActions}>
            <Button
              onClick={() => {}}
              appearance="text"
              color="dangerous"
              IconComponent={props => <FontAwesomeIcon icon={faTrashAlt} {...props} />}
              className={styles.sideButtons}
            >
              Delete
            </Button>
            <Button
              onClick={() => this.handleLoadSim({ _id, ...currentSimContent })}
              appearance="outline"
              length="long"
              IconComponent={props => <FontAwesomeIcon icon={faUpload} {...props} />}
              className={styles.sideButtons}
            >
              Load
            </Button>
          </div>
        </div>
      </>
    )
  }
}

UserSavedSimulations.propTypes = {
  redirect: PropTypes.func.isRequired,
  // props from connect()
  data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  dataFetched: PropTypes.bool.isRequired,
  dataLoading: PropTypes.bool.isRequired,
  getSavedSimulationsConnect: PropTypes.func.isRequired,
  loadSimFromAccountConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  data: state.self.savedSimulations.data,
  dataFetched: state.self.savedSimulations.fetched,
  dataLoading: state.self.savedSimulations.isLoading,
})

const mapDispatchToProps = {
  getSavedSimulationsConnect: getSavedSimulations,
  loadSimFromAccountConnect: loadSimFromAccount,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserSavedSimulations)
