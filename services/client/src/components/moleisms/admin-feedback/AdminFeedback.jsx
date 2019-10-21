/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Admin feedback page display of all feedback received.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import styles from './AdminFeedback.module.scss'

class AdminFeedback extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchName: '',
    }
  }

  componentDidMount = () => { }

  handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  render() {
    const { searchName } = this.state
    return (
      <div className={styles.container}>
        <h3>User Feedback</h3>
        <p>{searchName}</p>
      </div>
    )
  }
}

AdminFeedback.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
}

const mapStateToProps = state => ({})

const mapDispatchToProps = {}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
