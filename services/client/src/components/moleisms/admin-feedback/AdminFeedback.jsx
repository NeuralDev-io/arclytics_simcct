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
import { faEraser } from '@fortawesome/pro-light-svg-icons/faEraser'
import { getFeedback, searchFeedback } from '../../../state/ducks/feedback/actions'
import Button from '../../elements/button'
import { ControlledTable } from '../../elements/table'
import TextField from '../../elements/textfield'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'

import styles from './AdminFeedback.module.scss'


class AdminFeedback extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchQuery: '',
      isSearching: false,
      searchState: false,
    }
  }

  componentDidMount = () => { }

  fetchFeedbackQuery = (state) => {
    const { getFeedbackListConnect, searchFeedbackConnect } = this.props

    /*
    * These are the parameters from `state` sent by ControlledTable.
    *   - page: state.page, -- page (zero-indexed)
    *   - pageSize: state.pageSize, -- limit
    *   - sorted: state.sorted, -- sorting
    *     - Note: sorted ==> [ { "id": "...", "desc": bool } ]
    *   - filtered: state.filtered -- This one I don't need
    * */

    /*
    * Update the component state with the Redux state variables for the
    * ControlledTable so that when we search, we know exactly which params we
    * need to query with.
    * */
    const { searchState, searchQuery } = this.state

    // Set up sorting:
    let sort = '-created_date'
    if (state.sorted.length > 0) {
      if (state.sorted[0].desc) {
        sort = state.sorted[0].id
      } else {
        sort = `-${state.sorted[0].id}`
      }
    }

    if (searchState) {
      searchFeedbackConnect(
        `query=${searchQuery}&page=${state.page}&limit=${state.pageSize}&sort=${sort}`,
      )
    } else {
      getFeedbackListConnect(`page=${state.page}&limit=${state.pageSize}&sort=${sort}`)
    }
  }

  /**
   * This function just deals with the initial search request to the API server.
   * It's main purpose is to get the results and change the state of the Redux store
   * to one that is using search so that any time there is a change in the table,
   * we continue to use the search query for page changes rather than the default
   * retrieval of all data.
   */
  handleSearch = () => {
    this.setState({ isSearching: false, searchState: true })
    const { searchFeedbackConnect, sort, limit } = this.props
    const { searchQuery } = this.state
    // Make the initial search and get the first page.
    searchFeedbackConnect(
      `query=${searchQuery}&page=0&limit=${limit}&sort=${sort}`,
    )
  }

  /**
   * This function deals with clearing the search state and by retrieving the
   * full list of feedback again so the state of the table is back to normal.
   */
  handleClearSearch = () => {
    this.setState({ searchQuery: '', isSearching: false, searchState: false })
    const { getFeedbackListConnect, sort, limit } = this.props
    // Clear the table state by doing a retrieval of all the data again from
    // the first page.
    getFeedbackListConnect(`page=0&limit=${limit}&sort=${sort}`)
  }

  render() {
    const {
      isSearching,
      searchState,
      searchQuery,
    } = this.state

    const {
      dataFetched,
      dataLoading,
      totalPages,
    } = this.props
    // const { feedbackData: { sort: sortList, limit: limitList } } = this.props
    let { feedbackList } = this.props
    if (!dataFetched) feedbackList = []

    const columns = [
      {
        Header: 'Email',
        accessor: 'user',
        id: 'email',
        // Used to render a standard cell, defaults to `accessed` otherwise
        Cell: ({ value }) => value.email,
        sortable: false,
        filterable: false,
      },
      {
        Header: 'Category',
        accessor: 'category',
        id: 'category',
        maxWidth: 180,
      },
      {
        Header: 'Rating',
        accessor: 'rating',
        id: 'rating',
        maxWidth: 65,
      },
      {
        Header: 'Comment',
        accessor: 'comment',
        id: 'comment',
        minWidth: 180,
      },
      {
        Header: 'Created',
        accessor: 'created_date',
        id: 'created_date',
        Cell: ({ value }) => (<span>{dangerouslyGetDateTimeString(value)}</span>),
        maxWidth: 180,
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            {/*
            Potentially consider doing a send email feature as a response.
            <Button
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
          <TextField
            type="text"
            length="stretch"
            name="searchQuery"
            placeholder="Search feedback by email, category or comments..."
            value={searchQuery}
            onFocus={() => this.setState({ isSearching: true, searchState: true })}
            className={styles.searchBar}
            onChange={value => this.setState({ searchQuery: value })}
          />
          <Button
            appearance="outline"
            onClick={this.handleSearch}
            IconComponent={props => <FontAwesomeIcon icon={faSearch} {...props} />}
            length="long"
            className={styles.searchBtn}
            isDisabled={!isSearching}
          >
          Search
          </Button>
          <Button
            appearance="outline"
            onClick={this.handleClearSearch}
            IconComponent={props => <FontAwesomeIcon icon={faEraser} {...props} />}
            length="long"
            className={styles.clearBtn}
            isDisabled={!searchState}
          >
          Clear
          </Button>
        </div>

        <ControlledTable
          columns={columns}
          // Request new data when things change
          fetchData={this.fetchFeedbackQuery}
          data={feedbackList}
          pages={totalPages}
          loading={dataLoading}
          showPageSizeOptions={false}
          showPagination={feedbackList.length !== 0}
          resizable={false}
          defaultPageSize={10}
          condensed
          className="-highlight"
        />
      </div>
    )
  }
}

AdminFeedback.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  // These state params are managed by Redux store whether we are retrieving
  // or searching for feedback
  totalPages: PropTypes.number.isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  sort: PropTypes.string.isRequired,
  limit: PropTypes.number.isRequired,
  // Get parameters from Redux connect
  feedbackList: PropTypes.arrayOf(PropTypes.shape({
    user: PropTypes.shape({
      email: PropTypes.string,
    }),
    category: PropTypes.string,
    comment: PropTypes.string,
    rating: PropTypes.number,
    created_date: PropTypes.string,
  })).isRequired,
  getFeedbackListConnect: PropTypes.func.isRequired,
  // Search parameters from the Redux mapStateToProps connect
  searchData: PropTypes.shape({
    query: PropTypes.string,
    current_page: PropTypes.number,
  }).isRequired,
  searchFeedbackConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedbackList: state.feedback.feedbackList,
  dataFetched: state.feedback.isFetched,
  dataLoading: state.feedback.isLoading,
  totalPages: state.feedback.totalPages,
  sort: state.feedback.sort,
  limit: state.feedback.limit,
  getCurrentPage: state.feedback.feedbackData.current_page,
  searchData: state.feedback.searchData,
  searchCurrentPage: state.feedback.searchData.current_page,
})

const mapDispatchToProps = {
  getFeedbackListConnect: getFeedback,
  searchFeedbackConnect: searchFeedback,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
