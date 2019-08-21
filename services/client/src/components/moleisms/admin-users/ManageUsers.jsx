import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import SlashIcon from 'react-feather/dist/icons/slash'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import Table from '../../elements/table'
import { getUserProfile } from '../../../state/ducks/self/actions'

import styles from './ManageUsers.module.scss'

class ManageUsers extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchEmail: '',
    }
  }

  componentDidMount = () => {
    const { users, getUsersConnect } = this.props
    if (users.length === 0) getUsersConnect()
  }

  render() {
    const { searchEmail } = this.state
    const { users } = this.props
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
              onClick={() => console.log(original)}
              appearance="text"
              color={original.active ? 'dangerous' : 'default'}
              IconComponent={props => <SlashIcon {...props} />}
            >
              {original.active ? 'Deactivate' : 'Activate'}
            </Button>
          </div>
        ),
        width: 210,
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
  getUsersConnect: getUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(ManageUsers)
