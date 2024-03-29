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
/* eslint-disable react/jsx-props-no-spreading */
import React, { Component } from 'react'
// noinspection ES6CheckImport
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye } from '@fortawesome/pro-light-svg-icons/faEye'
import { faSearch } from '@fortawesome/pro-light-svg-icons/faSearch'
import { faEraser } from '@fortawesome/pro-light-svg-icons/faEraser'
import { faTimes } from '@fortawesome/pro-light-svg-icons/faTimes'
import { getFeedback, searchFeedback } from '../../../state/ducks/feedback/actions'
import Button, { IconButton } from '../../elements/button'
import { ControlledTable } from '../../elements/table'
import TextField from '../../elements/textfield'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'
import { getColor } from '../../../utils/theming'

import styles from './AdminFeedback.module.scss'


class AdminFeedback extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchQuery: '',
      isSearching: false,
      searchState: false,
      page: 0,
      showSideView: false,
      currentFeedback: {},
    }
  }

  componentDidMount = () => {}

  /**
   * The handle callback for React-Table that controls what happens when the state
   * of the table has changed.
   * @param (reactTableState) the state of the React-Table.
   */
  fetchFeedbackQuery = (reactTableState) => {
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
    let sort = 'created_date'
    if (reactTableState.sorted.length > 0) {
      if (reactTableState.sorted[0].desc) {
        sort = reactTableState.sorted[0].id
      } else {
        sort = `-${reactTableState.sorted[0].id}`
      }
    }

    if (searchState) {
      searchFeedbackConnect(
        `query=${searchQuery}&page=${reactTableState.page}&limit=${reactTableState.pageSize}&sort=${sort}`,
      )
    } else {
      getFeedbackListConnect(`page=${reactTableState.page}&limit=${reactTableState.pageSize}&sort=${sort}`)
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
    this.setState({ page: 0, isSearching: false, searchState: true })
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
    this.setState({
      page: 0,
      searchQuery: '',
      isSearching: false,
      searchState: false,
    })
    const { getFeedbackListConnect, sort, limit } = this.props
    // Clear the table state by doing a retrieval of all the data again from
    // the first page.
    getFeedbackListConnect(`page=0&limit=${limit}&sort=${sort}`)
  }

  handleViewSim = (feedback) => {
    const date = new Date(feedback.created_date)
    // eslint-disable-next-line no-underscore-dangle
    this.setState({
      showSideView: true,
      currentFeedback: {
        email: feedback.user.email,
        comment: feedback.comment,
        created: date.toString(),
        rating: feedback.rating,
        category: feedback.category,
      },
    })
    setTimeout(() => {
      this.setState({
        currentFeedback: {
          email: feedback.user.email,
          comment: feedback.comment,
          created: date.toString(),
          rating: feedback.rating,
          category: feedback.category,
        },
      })
    }, 500)
  }

  handleCloseSideView = () => {
    this.setState({
      showSideView: false,
      currentFeedback: {},
    })
  }

  render() {
    const {
      isSearching,
      searchState,
      searchQuery,
      page,
      showSideView,
      currentFeedback,
    } = this.state

    const {
      dataFetched,
      dataLoading,
      totalPages,
    } = this.props

    let { feedbackList = [] } = this.props
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
        maxWidth: 300,
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
        Header: 'Submitted',
        accessor: 'created_date',
        id: 'created_date',
        Cell: ({ value }) => (<span>{dangerouslyGetDateTimeString(value)}</span>),
        maxWidth: 180,
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
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
        width: 90, // 180, -- For 2 buttons
      },
    ]

    return (
      <>
        <div className={`${styles.mainView} ${showSideView ? styles.shrink : ''}`}>
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
            page={page}
            onPageChange={p => this.setState({ page: p })}
            loading={dataLoading}
            showPageSizeOptions={false}
            showPagination={feedbackList.length !== 0}
            resizable={false}
            defaultPageSize={10}
            condensed
            className="-highlight"
          />
        </div>
        <div className={`${styles.sideView} ${showSideView ? styles.show : ''}`}>
          <header className={styles.sideHeader}>
            <h5>
              Feedback from:
              {' '}
              {currentFeedback.email}
            </h5>
            <IconButton
              onClick={this.handleCloseSideView}
              Icon={props => <FontAwesomeIcon icon={faTimes} color={getColor('--n500')} {...props} />}
            />
          </header>

          <div className={styles.feedbackForm}>
            <h6>Submitted</h6>
            <p>{currentFeedback.created}</p>
            <br />
            <h6>Category</h6>
            <p>{currentFeedback.category}</p>
            <br />
            <h6>Rating</h6>
            <p>{currentFeedback.rating}</p>
            <br />
            <h6>Comment</h6>
            <p>{currentFeedback.comment}</p>
            <br />
          </div>

          <div className={styles.sideActions}>
            <Button
              onClick={this.handleCloseSideView}
              appearance="outline"
              length="long"
              IconComponent={props => <FontAwesomeIcon icon={faTimes} {...props} />}
              className={styles.sideButtons}
            >
                Close
            </Button>
          </div>
        </div>
      </>
    )
  }
}

AdminFeedback.propTypes = {
  // These state params are managed by Redux store whether we are retrieving
  // or searching for feedback
  totalPages: PropTypes.number.isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  sort: PropTypes.string.isRequired,
  limit: PropTypes.number.isRequired,
  page: PropTypes.number.isRequired,
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
  searchData: state.feedback.searchData,
})

const mapDispatchToProps = {
  getFeedbackListConnect: getFeedback,
  searchFeedbackConnect: searchFeedback,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
