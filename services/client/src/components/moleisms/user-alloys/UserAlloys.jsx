import React, { Component } from 'react'

import styles from './UserAlloys.module.scss'

class UserAlloys extends Component {
  // constructor(props) {
  //   super(props)
  //   this.state = {
  //     name: '',
  //   }
  // }

  render() {
    return (
      <div className={styles.container}>
        <h3>Personal Alloy database</h3>
      </div>
    )
  }
}

export default UserAlloys
