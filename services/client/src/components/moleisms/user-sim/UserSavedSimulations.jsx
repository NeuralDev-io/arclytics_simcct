import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import EyeIcon from 'react-feather/dist/icons/eye'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Button from '../../elements/button'
import Table from '../../elements/table'
import { getSavedSimulations } from '../../../state/ducks/self/actions'

import styles from './UserSavedSimulations.module.scss'

class UserSavedSimulations extends Component {
  componentDidMount = () => {
    const { data, getSavedSimulationsConnect } = this.props
    if (data.length === 0) getSavedSimulationsConnect()
  }

  render() {
    const { data } = this.props
    const columns = [
      {
        Header: 'ID',
        accessor: '_id',
      },
      {
        Header: '',
        Cell: () => (
          <div className={styles.actions}>
            <Button
              onClick={() => {}}
              appearance="text"
              length="short"
              IconComponent={props => <EyeIcon {...props} />}
            >
              View
            </Button>
            <Button
              onClick={() => {}}
              appearance="text"
              color="dangerous"
              IconComponent={props => <TrashIcon {...props} />}
            >
              Delete
            </Button>
          </div>
        ),
        width: 210,
      },
    ]

    return (
      <div className={styles.container}>
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
    )
  }
}

UserSavedSimulations.propTypes = {
  // props from connect()
  data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  getSavedSimulationsConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  data: state.self.savedSimulations,
})

const mapDispatchToProps = {
  getSavedSimulationsConnect: getSavedSimulations,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserSavedSimulations)
