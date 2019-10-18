/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Global users display
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus } from '@fortawesome/pro-light-svg-icons/faPlus'
import { faEdit } from '@fortawesome/pro-light-svg-icons/faEdit'
import { faUpload } from '@fortawesome/pro-light-svg-icons/faUpload'
import { faUserSlash } from '@fortawesome/pro-light-svg-icons/faUserSlash'
import { faUserCheck } from '@fortawesome/pro-light-svg-icons/faUserCheck'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import Table from '../../elements/table'
import SecureConfirmModal from '../confirm-modal/SecureConfirmModal'
import Modal from '../../elements/modal'
import { getUsers, promoteAdmin, deactivateUser, enableUser } from '../../../state/ducks/users/actions'

import styles from './ManageUsers.module.scss'
import ProfilePage from "../user-profile";

class ManageUsers extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchEmail: '',
      showPromoteModal: false,
      promoteName: '',
      promoteEmail: '',

    }
  }

  componentDidMount = () => {
    const {users, getUsersConnect} = this.props
    if (users.length === 0) getUsersConnect()
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }
  /**
   *
   * @param name - optional
   * @param email - optional
   */
  handleShowPromoteModal = (name, email) => {
    const { showPromoteModal } = this.state
    if (showPromoteModal === false){
      this.setState({
        promoteName: name,
        promoteEmail: email,
        showPromoteModal: true,
      })
    }
  }


  handlePromoteSubmit = (email) => {
    const {getUsersConnect, promoteAdminConnect} = this.props
    console.log(email)
    promoteAdminConnect(email)
    this.setState( {
      promoteName: '',
      promoteEmail: '',
      showPromoteModal: false
    })
  }

  handleActivateSubmit = (email, isActive) => {
    const { deactivateUserConnect, getUsersConnect, enableUserConnect } = this.props
    console.log(email)
    if (isActive){
      deactivateUserConnect(email)
      getUsersConnect()
    } else if (!isActive){
      enableUserConnect(email)
    }
  }


  render() {
    const {searchEmail, showPromoteModal, promoteName, deactivateUserConnect } = this.state
    const {users,} = this.props
    const tableData = users.filter(u => u.email.includes(searchEmail))

    const columns = [
      {
        Header: 'Email',
        accessor: 'email',
      },
      {
        Header: 'Full name',
        Cell: ({original}) => <span>{[original.first_name, original.last_name].join(' ')}</span>,
      },
      {
        Header: 'Admin',
        accessor: 'admin',
        Cell: ({value}) => <span>{value ? 'Yes' : 'No'}</span>,
        width: 80,
      },
      {
        Header: 'Verified',
        accessor: 'verified',
        Cell: ({value}) => <span>{value ? 'Yes' : 'No'}</span>,
        width: 80,
      },
      {
        Header: '',
        Cell: ({original}) => (
          <div className={styles.actions}>
            <Button
              onClick={() => console.log(original)}
              appearance="text"
              length="short"
              IconComponent={props => <FontAwesomeIcon icon={faEdit} size="6x" {...props} />}
            >
              Edit
            </Button>

            <Button
              onClick={() => {
                this.handleShowPromoteModal(`${original.first_name} ${original.last_name}`, original.email)
              }}
              appearance="text"
              IconComponent={props => <FontAwesomeIcon icon={faUserCheck} size="lg" {...props}/>}
              isDisabled={original.admin}
            >
              Promote
            </Button>

            <Button
              onClick={() => this.handleActivateSubmit(original.email, original.active)}
              appearance="text"
              isDisabled={original.admin}
              color={original.active ? 'dangerous' : 'default'}
              IconComponent={props => <FontAwesomeIcon icon={faUserSlash} size="lg" {...props} />}
            >
              {original.active ? 'Deactivate' : 'Activate'}
            </Button>
          </div>
        ),
        width: 337,
      },
    ]

    return (
      <div className={styles.container}>
        <h3>Users</h3>
        <div className={styles.tools}>
          <div className="input-row">
            <span>Search</span>
            <TextField
              type="text"
              length="long"
              name="searchEmail"
              placeholder="Email..."
              value={searchEmail}
              onChange={value => this.setState({searchEmail: value})}
            />
          </div>
          <Button
            appearance="outline"
            onClick={this.showAddAlloy}
            IconComponent={props => <FontAwesomeIcon icon={faPlus} size="lg"{...props} />}
            length="short"
          >
            Add
          </Button>
        </div>
        <Table
          className="-highlight"
          data={tableData}
          columns={columns}
          pageSize={tableData.length > 10 ? 10 : tableData.length}
          showPageSizeOptions={false}
          showPagination={tableData.length !== 0}
          resizable={false}
          condensed
        />

        <SecureConfirmModal
          onClick={() => {
            this.handlePromote()
          }}
          show={showPromoteModal}
          messageTitle={`Promote '${this.state.promoteName}' to admin ?`}
          actionButtonName="Confirm Promote"
          onSubmit = {() => this.handlePromoteSubmit(this.state.promoteEmail)}
          onClose = {() => this.setState({showPromoteModal: false})}
        />
      </div>
    )
  }
}


ManageUsers.propTypes = {
  users: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  getUsersConnect: PropTypes.func.isRequired,
  promoteAdminConnect: PropTypes.func.isRequired,
  deactivateUserConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  users: state.users,
})

const mapDispatchToProps = {
  getUsersConnect: getUsers,
  promoteAdminConnect: promoteAdmin,
  deactivateUserConnect: deactivateUser,
  enableUserConnect: enableUser,
}

export default connect(mapStateToProps, mapDispatchToProps)(ManageUsers)
