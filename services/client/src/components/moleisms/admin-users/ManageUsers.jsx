import React, { Component } from 'react'
import { connect } from 'react-redux'
import PeriodicTable from '../../elements/periodic-table'

import styles from './ManageUsers.module.scss'

class ManageUsers extends Component {
  componentDidMount = () => {}

  render() {
    return (
      <div className={styles.container}>
        <h3>Users</h3>
        <PeriodicTable />
      </div>
    )
  }
}

ManageUsers.propTypes = {

}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(ManageUsers)
