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
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import SlashIcon from 'react-feather/dist/icons/slash'
import PromoteIcon from 'react-feather/dist/icons/user-check'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import Table from '../../elements/table'
import SecureConfirmModal from '../confirm-modal/SecureConfirmModal'
import Modal from '../../elements/modal'
import { getUsers, promoteAdmin } from '../../../state/ducks/users/actions'

import styles from './ManageUsers.module.scss'

class ManageUsers extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchEmail: '',
      promoteConfirmModal: false,
    }
  }

  componentDidMount = () => {
    const { users, getUsersConnect } = this.props
    if (users.length === 0) getUsersConnect()
  }

  handlePromote (email) {
    const { getUsersConnect, promoteAdminConnect} = this.props
    // promoteAdminConnect(email)
    return (
      <SecureConfirmModal
        // this.handlePromote(original.email)
        onClick={() => {this.handlePromote(email)}}
        show
        onClose={() => {this.setState({ promoteConfirmModal: false})}}
      >
        <div>
          sucks to suck
        </div>
      </SecureConfirmModal>
    )
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  handleShowConfirmModal = (name, email) => {
    const { promoteConfirmModal } = this.state

     if (promoteConfirmModal) {
       return (
           <SecureConfirmModal
             // this.handlePromote(original.email)
             onClick={() => {this.handlePromote(email)}}
             show
             onClose={() => {this.setState({ promoteConfirmModal: false})}}
           >
             <div>
               sucks to suck
             </div>
           </SecureConfirmModal>
         )
     }

  }

  render() {
    const { searchEmail, promoteConfirmModal } = this.state
    const { users, } = this.props
    const tableData = users.filter(u => u.email.includes(searchEmail))

    const columns = [
      {
        Header: 'Email',
        accessor: 'email',
      },
      {
        Header: 'Full name',
        Cell: ({ original }) => <span>{[original.first_name, original.last_name].join(' ')}</span>,
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
        width: 80,
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
              onClick={() => console.log(original)}
              appearance="text"
              length="short"
              IconComponent={props => <EditIcon {...props} />}
            >
              Edit
            </Button>
            <Button
              onClick={() => {this.setState({promoteConfirmModal: true})}}
              appearance="text"
              IconComponent={props => <PromoteIcon {...props}/>}
              isDisabled={original.admin}
            >
              Promote
            </Button>

            <SecureConfirmModal
              onClick={() => {this.handlePromote(original.email)}}
              show={promoteConfirmModal}
              onClose={() => {this.setState({ promoteConfirmModal: false})}}
            >
              <div>
                Do you want to promote the user {original.first}&nbsp;{original.last}?
              </div>
            </SecureConfirmModal>

            <Button
              onClick={() => console.log(original)}
              appearance="text"
              isDisabled={original.admin}
              color={original.active ? 'dangerous' : 'default'}
              IconComponent={props => <SlashIcon {...props} />}
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
              onChange={value => this.setState({ searchEmail: value })}
            />
          </div>
          <Button
            appearance="outline"
            onClick={this.showAddAlloy}
            IconComponent={props => <PlusIcon {...props} />}
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
      </div>
    )
  }
}

ManageUsers.propTypes = {
  users: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  getUsersConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  users: state.users,
})

const mapDispatchToProps = {
  getUsersConnect: getUsers,
  promoteAdminConnect: promoteAdmin
}

export default connect(mapStateToProps, mapDispatchToProps)(ManageUsers)
