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
import { ControlledTable } from '../../elements/table'
import TextField from '../../elements/textfield'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'

import styles from './AdminFeedback.module.scss'

/*
* TODO:
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

  componentDidMount = () => { }

  // handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  // handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  fetchFeedbackQuery = (state) => {
    const {
      getFeedbackListConnect,
      sort,
    } = this.props

    /*
    * page: state.page, -- page (zero-indexed)
    * pageSize: state.pageSize, -- limit
    * sorted: state.sorted, -- sorting
    *  - Note: sorted ==> [ { "id": "...", "desc": bool } ]
    * filtered: state.filtered -- This one I don't need
    *
    * */
    // console.log(state.sorted)

    getFeedbackListConnect(`limit=${state.pageSize}&page=${state.page}&sort=${sort}`)

    // if (currentPage < state.page) {
    //   Forward
      // getFeedbackListConnect(`limit=${state.pageSize}&offset=${nextOffset}&sort=${sort}`)
      // this.setState({ currentPage: state.page })
    // } else {
    //   Back
      // getFeedbackListConnect(`limit=${state.pageSize}&offset=${prevOffset}&sort=${sort}`)
      // this.setState({ currentPage: state.page })
    // }
  }

  render() {
    // First check if we have any data to render or set to empty
    const {
      dataFetched,
      dataLoading,
      currentPage,
      totalPages,
      limit,
    } = this.props
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

        <ControlledTable
          columns={columns}
          // Forces table not to paginate or sort automatically,
          // so we can handle it server-side
          // Request new data when things change
          fetchData={this.fetchFeedbackQuery}
          data={feedbackData}
          pages={totalPages}
          loading={dataLoading}
          showPageSizeOptions={false}
          // showPagination={feedbackData.length !== 0}
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
  feedbackData: PropTypes.arrayOf(PropTypes.shape({
    user: PropTypes.shape({
      email: PropTypes.string,
    }),
    category: PropTypes.string,
    comment: PropTypes.string,
    rating: PropTypes.number,
    created_date: PropTypes.string,
  })).isRequired,
  sort: PropTypes.string.isRequired,
  limit: PropTypes.number.isRequired,
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  getFeedbackListConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedbackData: state.feedback.feedbackList.data,
  sort: state.feedback.feedbackList.sort,
  limit: state.feedback.feedbackList.limit,
  currentPage: state.feedback.feedbackList.current_page,
  totalPages: state.feedback.feedbackList.total_pages,
  dataLoading: state.feedback.feedbackList.isLoading,
  dataFetched: state.feedback.feedbackList.isFetched,
})

const mapDispatchToProps = {
  getFeedbackListConnect: getFeedback,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminFeedback)
