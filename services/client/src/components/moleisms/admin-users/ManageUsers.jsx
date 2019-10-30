/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Global users display
 *
 * @version 1.0.0
 * @author Dalton Le, Andrew Che, Arvy Salazar
 */
/* eslint-disable react/jsx-props-no-spreading */
import React, { Component } from 'react'
// noinspection ES6CheckImport
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch } from '@fortawesome/pro-light-svg-icons/faSearch'
import { faEraser } from '@fortawesome/pro-light-svg-icons/faEraser'
import { faUserSlash } from '@fortawesome/pro-light-svg-icons/faUserSlash'
import { faUserCheck } from '@fortawesome/pro-light-svg-icons/faUserCheck'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { ControlledTable } from '../../elements/table'
import SecureConfirmModal from '../confirm-modal/SecureConfirmModal'
import UserPromoteModal from './UserPromoteModal'
import {
  getUsers,
  promoteAdmin,
  deactivateUser,
  enableUser, searchUsers,
} from '../../../state/ducks/users/actions'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'

import styles from './ManageUsers.module.scss'


class ManageUsers extends Component {
  constructor(props) {
    super(props)
    this.state = {
      page: 0,
      isSearching: false,
      searchState: false,
      searchQuery: '',
      showPromoteModal: false,
      promoteName: '',
      promoteEmail: '',
      showStatusModal: false,
      statusIsActive: '',
      statusName: '',
      statusEmail: '',
    }
  }

  componentDidMount = () => { }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  handleShowPromoteModal = (name, email) => {
    const { showPromoteModal } = this.state
    if (showPromoteModal === false) {
      this.setState({
        showPromoteModal: true,
        promoteName: name,
        promoteEmail: email,
      })
    }
  }

  handlePromoteSubmit = (email, position) => {
    const { promoteAdminConnect } = this.props
    promoteAdminConnect(email, position)
    this.setState({
      promoteName: '',
      promoteEmail: '',
      showPromoteModal: false,
    })
  }

  handleShowStatusModal = (name, email, active) => {
    const { showStatusModal } = this.state
    if (showStatusModal === false) {
      this.setState({
        showStatusModal: true,
        statusIsActive: active,
        statusName: name,
        statusEmail: email,
      })
    }
  }

  handleStatusSubmit = (email, isActive) => {
    const { deactivateUserConnect, getUsersConnect, enableUserConnect } = this.props
    if (isActive) {
      deactivateUserConnect(email)
    } else if (!isActive) {
      enableUserConnect(email)
      getUsersConnect()
    }
    this.setState({
      showStatusModal: false,
      statusIsActive: '',
      statusName: '',
      statusEmail: '',
    })
  }

  /**
   * The handle callback for React-Table that controls what happens when the state
   * of the table has changed.
   * @param (reactTableState) the state of the React-Table.
   */
  fetchUsersQuery = (reactTableState) => {
    const { getUsersConnect, searchUsersConnect } = this.props

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
      searchUsersConnect(
        `query=${searchQuery}&page=${reactTableState.page}&limit=${reactTableState.pageSize}
        &sort=${sort}`,
      )
    } else {
      getUsersConnect(`page=${reactTableState.page}&limit=${reactTableState.pageSize}&sort=${sort}`)
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
    const { searchUsersConnect, sort, limit } = this.props
    const { searchQuery } = this.state
    // Make the initial search and get the first page.
    searchUsersConnect(
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
    const { getUsersConnect, sort, limit } = this.props
    // Clear the table state by doing a retrieval of all the data again from
    // the first page.
    getUsersConnect(`page=0&limit=${limit}&sort=${sort}`)
  }

  render() {
    const {
      isSearching,
      searchState,
      searchQuery,
      page,
      showPromoteModal,
      promoteName,
      promoteEmail,
      showStatusModal,
      statusIsActive,
      statusName,
      statusEmail,
    } = this.state
    const {
      dataFetched,
      dataLoading,
      totalPages,
    } = this.props

    let { users = [] } = this.props
    if (!dataFetched || users.length === 0) users = []

    const columns = [
      {
        Header: 'Email',
        accessor: 'email',
        minWidth: 240,
      },
      {
        Header: 'Full name',
        id: 'full_name',
        Cell: ({ original }) => <span>{[original.first_name, original.last_name].join(' ')}</span>,
        minWidth: 240,
      },
      {
        Header: 'Joined',
        accessor: 'created',
        // The search param accepted in the backend is created_date
        id: 'created_date',
        Cell: ({ value }) => (<span>{dangerouslyGetDateTimeString(value)}</span>),
        width: 180,
      },
      {
        Header: 'Admin',
        accessor: 'admin',
        Cell: ({ value }) => <span>{value ? 'Yes' : 'No'}</span>,
        width: 80,
      },
      {
        Header: 'Verified',
        accessor: 'verified',
        Cell: ({ value }) => <span>{value ? 'Yes' : 'No'}</span>,
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
              onClick={() => {
                this.handleShowPromoteModal(`${original.first_name} ${original.last_name}`, original.email)
              }}
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faUserCheck} size="lg" {...props} />}
              isDisabled={original.admin}
            >
              Promote
            </Button>

            <Button
              onClick={() => {
                this.handleShowStatusModal(
                  `${original.first_name} ${original.last_name}`,
                  original.email,
                  original.active,
                )
              }}
              appearance="text"
              isDisabled={original.admin}
              color={original.active ? 'dangerous' : 'default'}
              IconComponent={props => <FontAwesomeIcon icon={faUserSlash} size="lg" {...props} />}
            >
              {original.active ? 'Disable' : 'Enable'}
            </Button>
          </div>
        ),
        width: 280,
      },
    ]

    return (
      <div className={styles.container}>
        <h3>Users</h3>

        <div className={styles.tools}>
          <TextField
            type="text"
            length="stretch"
            name="searchQuery"
            placeholder="Search users by email, first or last name..."
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
          fetchData={this.fetchUsersQuery}
          data={users}
          pages={totalPages}
          page={page}
          onPageChange={p => this.setState({ page: p })}
          loading={dataLoading}
          showPageSizeOptions={false}
          showPagination={totalPages > 1}
          resizable={false}
          defaultPageSize={10}
          condensed
          className="-highlight"
        />

        <UserPromoteModal
          show={showPromoteModal}
          messageTitle={`Promote '${promoteName}' to admin ?`}
          actionButtonName="Confirm Promote"
          email={promoteEmail}
          onSubmit={(email, position) => this.handlePromoteSubmit(email, position)}
          onClose={() => this.setState({ showPromoteModal: false })}
        />
        <SecureConfirmModal
          show={showStatusModal}
          messageTitle={
            statusIsActive
              ? `Do you want to deactivate '${statusName}' ?`
              : `Do you want to activate '${statusName}' ?`
          }
          actionButtonName={statusIsActive ? 'Deactivate' : 'Activate'}
          onSubmit={() => this.handleStatusSubmit(statusEmail, statusIsActive)}
          onClose={() => this.setState({ showStatusModal: false })}
          isDangerous
        />
      </div>
    )
  }
}


ManageUsers.propTypes = {
  users: PropTypes.arrayOf(PropTypes.shape({
    email: PropTypes.string,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    active: PropTypes.bool,
    admin: PropTypes.bool,
    verified: PropTypes.bool,
    created: PropTypes.string,
  })).isRequired,
  totalPages: PropTypes.number.isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  sort: PropTypes.string.isRequired,
  limit: PropTypes.number.isRequired,
  getUsersConnect: PropTypes.func.isRequired,
  searchUsersConnect: PropTypes.func.isRequired,
  promoteAdminConnect: PropTypes.func.isRequired,
  enableUserConnect: PropTypes.func.isRequired,
  deactivateUserConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  users: state.users.usersList,
  dataFetched: state.users.isFetched,
  dataLoading: state.users.isLoading,
  totalPages: state.users.totalPages,
  sort: state.users.sort,
  limit: state.users.limit,
  searchData: state.users.searchData,
})

const mapDispatchToProps = {
  getUsersConnect: getUsers,
  searchUsersConnect: searchUsers,
  promoteAdminConnect: promoteAdmin,
  deactivateUserConnect: deactivateUser,
  enableUserConnect: enableUser,
}

export default connect(mapStateToProps, mapDispatchToProps)(ManageUsers)
