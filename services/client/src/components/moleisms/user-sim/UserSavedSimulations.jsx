import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import EyeIcon from 'react-feather/dist/icons/eye'
import UploadIcon from 'react-feather/dist/icons/upload'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import XIcon from 'react-feather/dist/icons/x'
import Button, { IconButton } from '../../elements/button'
import Table from '../../elements/table'
import { getSavedSimulations } from '../../../state/ducks/self/actions'
import { loadSimFromAccount } from '../../../state/ducks/sim/actions'

import styles from './UserSavedSimulations.module.scss'

class UserSavedSimulations extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showSideView: false,
      currentSim: {},
    }
  }

  componentDidMount = () => {
    const { data = [], getSavedSimulationsConnect } = this.props
    if (data.length === 0) getSavedSimulationsConnect()
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
    this.setState({ showSideView: true, currentSim: { _id: sim._id } })
    setTimeout(() => {
      this.setState({
        // showSideView: true,
        currentSim: sim,
      })
    }, 500)
    // this.setState({
    //   // showSideView: true,
    //   currentSim: sim,
    // })
  }

  handleCloseSideView = () => {
    this.setState({
      showSideView: false,
      currentSim: {},
    })
  }

  render() {
    const { showSideView, currentSim: { _id, ...currentSimContent } } = this.state
    const { data = [] } = this.props
    const columns = [
      {
        Header: 'ID',
        accessor: '_id',
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
              onClick={() => this.handleLoadSim(original)}
              length="short"
              appearance="text"
              IconComponent={props => <UploadIcon {...props} />}
            >
              Load
            </Button>
            <Button
              onClick={() => this.handleViewSim(original)}
              length="short"
              appearance="text"
              IconComponent={props => <EyeIcon {...props} />}
            >
              View
            </Button>
          </div>
        ),
        width: 180,
      },
    ]

    return (
      <React.Fragment>
        <div className={`${styles.mainview} ${showSideView ? styles.shrink : ''}`}>
          <h3>Saved simulations</h3>
          <Table
            className="-highlight"
            data={data}
            columns={columns}
            pageSize={data.length > 10 ? 10 : data.length}
            showPageSizeOptions={false}
            showPagination={data.length !== 0}
            resizable={false}
            condensed
          />
        </div>
        <div className={`${styles.sideview} ${showSideView ? styles.show : ''}`}>
          <header className={styles.sideHeader}>
            <h5>Sim ID: {_id}</h5>
            <IconButton
              onClick={this.handleCloseSideView}
              Icon={props => <XIcon {...props} />}
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
              IconComponent={props => <TrashIcon {...props} />}
              className={styles.sideButtons}
            >
              Delete
            </Button>
            <Button
              onClick={() => this.handleLoadSim({ _id, ...currentSimContent })}
              appearance="outline"
              length="long"
              IconComponent={props => <UploadIcon {...props} />}
              className={styles.sideButtons}
            >
              Load
            </Button>
          </div>
        </div>
      </React.Fragment>
    )
  }
}

UserSavedSimulations.propTypes = {
  redirect: PropTypes.func.isRequired,
  // props from connect()
  data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  getSavedSimulationsConnect: PropTypes.func.isRequired,
  loadSimFromAccountConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  data: state.self.savedSimulations,
})

const mapDispatchToProps = {
  getSavedSimulationsConnect: getSavedSimulations,
  loadSimFromAccountConnect: loadSimFromAccount,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserSavedSimulations)
