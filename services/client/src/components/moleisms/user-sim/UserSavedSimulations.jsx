import React, { Component } from 'react'

import styles from './UserSavedSimulations.module.scss'

class UserSavedSimulations extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  render() {
    // const { name } = this.state

    // console.log(alloyList, name)
    // const tableData = alloyList.filter(a => a.name.includes(name))
    // console.log(tableData)

    return (
      <div className={styles.container}>
        <h3>Personal Saved Simulation</h3>
      </div>
    )
  }
}

export default UserSavedSimulations
