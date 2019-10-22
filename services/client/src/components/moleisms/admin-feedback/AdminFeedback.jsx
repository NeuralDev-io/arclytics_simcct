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
import { getFeedback } from '../../../state/ducks/feedback/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'

class AdminFeedback extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchName: '',
    }
  }

  componentDidMount = () => {
    const {
      feedbackData = [],
      dataFetched = false,
      getFeedbackListConnect,
      addFlashToastConnect,
    } = this.props

    if (!feedbackData || feedbackData.length === 0 || !dataFetched) {
      getFeedbackListConnect('limit=10&offset=1&sort=created_date')
    }
  }

  // handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  // handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  render() {
    // First check if we have any data to render or set to empty
    const { dataFetched, dataLoading } = this.props
    let { feedbackData } = this.props
    if (!dataFetched) feedbackData = []

    // const { searchName } = this.state
    console.log(feedbackData)

    return (
      <div className={styles.container}>
        <h3>User feedback</h3>
        <h5>
          Data Loading:
          {' '}
          {dataLoading ? 'true' : 'false'}
        </h5>
        <h5>
          Data Fetched:
          {' '}
          {!dataFetched ? 'none' : feedbackData.length}
        </h5>
      </div>
    )
  }
}

/*
* TODO(andrew@neuraldev.io): add the required pagination state
*  - sort, offset, limit, next_offset, prev_offset, n_results, current_page, total_pages
* */
AdminFeedback.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  feedbackData: PropTypes.arrayOf(PropTypes.shape({
    email: PropTypes.string,
    category: PropTypes.string,
    rating: PropTypes.number,
    comment: PropTypes.string,
    created_date: PropTypes.instanceOf(Date),
  })).isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  getFeedbackListConnect: PropTypes.func.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedbackData: state.feedback.feedbackList.data,
  dataLoading: state.feedback.feedbackList.isLoading,
  dataFetched: state.feedback.feedbackList.isFetched,
})

const mapDispatchToProps = {
  getFeedbackListConnect: getFeedback,
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
