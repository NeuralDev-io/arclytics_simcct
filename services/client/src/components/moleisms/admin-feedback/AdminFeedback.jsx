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
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye } from '@fortawesome/pro-light-svg-icons/faEye'
import { faSearch } from '@fortawesome/pro-light-svg-icons/faSearch'
import { getFeedback } from '../../../state/ducks/feedback/actions'
import Button from '../../elements/button'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'

import styles from './AdminFeedback.module.scss'

/*
* TODO:
*  - Build the table.
*  - Add the pagination param variables to Redux state
*  - Add pagination callback to ReactTable component
*
* */

class AdminFeedback extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchQuery: '',
      isSearching: false,
    }
  }

  componentDidMount = () => {
    const {
      feedbackData = [],
      dataFetched = false,
      getFeedbackListConnect,
      offset,
      limit,
      sort,
    } = this.props

    if (!feedbackData || feedbackData.length === 0 || !dataFetched) {
      getFeedbackListConnect(`limit=${limit}&offset=${offset}&sort=${sort}`)
    }
  }

  // handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  // handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  render() {
    // First check if we have any data to render or set to empty
    const { dataFetched, dataLoading } = this.props
    let { feedbackData } = this.props
    if (!dataFetched) feedbackData = []

    const {
      isSearching,
      searchQuery,
    } = this.state

    const columns = [
      {
        Header: 'Email',
        accessor: 'user',
        // Used to render a standard cell, defaults to `accessed` otherwise
        Cell: ({ value }) => value.email,
        // sortMethod: () => {},
      },
      {
        Header: 'Category',
        accessor: 'category',
        maxWidth: 180,
      },
      {
        Header: 'Rating',
        accessor: 'rating',
        maxWidth: 65,
      },
      {
        Header: 'Comment',
        accessor: 'comment',
        // width: 100,
        minWidth: 180,
      },
      {
        Header: 'Created',
        accessor: 'created_date',
        Cell: ({ value }) => (<span>{dangerouslyGetDateTimeString(value)}</span>),
        maxWidth: 180,
      },
      // May need a button for viewing the full content.
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            {/* <Button
              onClick={() => this.handleLoadSim(original)}
              length="short"
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faUpload} {...props} />}
            >
              Load
            </Button> */}
            <Button
              onClick={() => console.log(original)}
              length="short"
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faEye} {...props} />}
            >
              View
            </Button>
          </div>
        ),
        width: 90, // 180, -- For 2 buttons
      },
    ]

    return (
      <div className={styles.container}>
        <h3>User feedback</h3>

        <div className={styles.tools}>
          <div className="input-row">
            <span>Search</span>
            <TextField
              type="text"
              length="long"
              name="searchQuery"
              placeholder="Search feedback..."
              value={searchQuery}
              onChange={value => this.setState({ searchQuery: value })}
            />
          </div>
          <Button
            appearance="outline"
            onClick={() => console.log('Search')}
            IconComponent={props => <FontAwesomeIcon icon={faSearch} {...props} />}
            length="long"
            isDisabled={!isSearching}
          >
            Search
          </Button>
        </div>

        <Table
          className="-highlight"
          data={feedbackData}
          columns={columns}
          loading={dataLoading}
          pageSize={feedbackData.length > 10 ? 10 : feedbackData.length}
          showPageSizeOptions={false}
          showPagination={feedbackData.length !== 0}
          resizable={false}
          condensed
        />
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
    user: PropTypes.shape({
      email: PropTypes.string,
    }),
    category: PropTypes.string,
    comment: PropTypes.string,
    rating: PropTypes.number,
    created_date: PropTypes.instanceOf(Date),
  })).isRequired,
  sort: PropTypes.string,
  offset: PropTypes.number,
  limit: PropTypes.number,
  next_offset: PropTypes.number,
  prev_offset: PropTypes.number,
  current_page: PropTypes.number,
  total_pages: PropTypes.number,
  n_results: PropTypes.number,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  getFeedbackListConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedbackData: state.feedback.feedbackList.data,
  sort: state.feedback.feedbackList.sort,
  offset: state.feedback.feedbackList.offset,
  limit: state.feedback.feedbackList.limit,
  next_offset: state.feedback.feedbackList.next_offset,
  prev_offset: state.feedback.feedbackList.prev_offset,
  current_page: state.feedback.feedbackList.current_page,
  total_pages: state.feedback.feedbackList.total_pages,
  n_results: state.feedback.feedbackList.n_results,
  dataLoading: state.feedback.feedbackList.isLoading,
  dataFetched: state.feedback.feedbackList.isFetched,
})

const mapDispatchToProps = {
  getFeedbackListConnect: getFeedback,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
