/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * A component that displays the list of User Alloys from the User's Document
 * with associated operations including create, update, and delete.
 *
 * @version 0.2.0
 * @author Andrew Che
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import UserAlloyDeleteModal from './UserAlloyDeleteModal'
import {
  createUserAlloy,
  getUserAlloys,
  updateUserAlloy,
  deleteUserAlloy,
} from '../../../state/ducks/alloys/actions'

import styles from './UserAlloys.module.scss'

class UserAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      name: '',
      currentAlloy: {},
      addModal: false,
      editModal: false,
      deleteModal: false,
    }
  }

  componentDidMount() {
    // Put a guard on this page if there's no token.
    if (!localStorage.getItem('token')) {
      this.props.history.push('/signin')
    }
    // When the component mounts, we need to get the list of alloys with API first.
    const { alloyList, getAlloysConnect } = this.props
    if (!alloyList || alloyList.length === 0) getAlloysConnect()
  }

  // We change the boolean that shows the Modal for the correct Modal Option
  // but we also set the current Rows Original alloy data to currentAlloy so the
  // callback can update/delete the right one.
  handleShowModal = (type, alloy) => this.setState({ [`${type}Modal`]: true, currentAlloy: alloy })

  // Do the reverse of above and remove currentAlloy
  handleCloseModal = type => this.setState({ [`${type}Modal`]: false, currentAlloy: {} })

  handleAlloyOperation = (option) => {
    const { getAlloysConnect, deleteAlloysConnect } = this.props

    if (option === 'add') console.log('add')

    if (option === 'edit') console.log('edit')

    if (option === 'delete') {
      this.handleCloseModal('delete')
      deleteAlloysConnect(this.state.currentAlloy.alloyId)
    }
  }

  render() {
    const { alloyList } = this.props
    const { name, deleteModal } = this.state

    // Prepare the data for the Table component
    // const tableData = alloyList.filter(a => a.name.includes(name))
    const tableData = alloyList.map(alloy => ({
      // eslint-disable-next-line no-underscore-dangle
      alloyId: alloy._id,
      name: alloy.name,
      compositions: alloy.compositions,
    }))
    const columns = [
      {
        Header: 'Alloy name',
        accessor: 'name',
      },
      {
        Header: '',
        // Each cell gets the original data passed to it from the tableData mapping
        Cell: (({ original }) => (
          <div className={styles.actions}>
            <Button
              appearance="text"
              onClick={() => this.handleShowModal('edit')}
              length="short"
              IconComponent={props => <EditIcon {...props} />}
            >
              Edit
            </Button>
            <Button
              appearance="text"
              onClick={() => this.handleShowModal('delete', original)}
              color="dangerous"
              IconComponent={props => <TrashIcon {...props} />}
            >
              Delete
            </Button>
          </div>
        )),
        width: 210,
      },
    ]

    return (
      <div className={styles.container}>
        <h3>Personal alloy database</h3>
        <div className={styles.tools}>
          <div className="input-row">
            <span>Search</span>
            <TextField
              type="text"
              length="long"
              name="name"
              placeholder="Alloy name"
              value={name}
              onChange={value => this.setState({ name: value })}
            />
          </div>
          <Button
            appearance="outline"
            onClick={() => this.handleShowModal('add')}
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

        <UserAlloyDeleteModal
          show={deleteModal}
          onConfirm={() => this.handleAlloyOperation('delete')}
          onClose={() => this.handleCloseModal('delete')}
        />
      </div>
    )
  }
}

// Type annotate props
UserAlloys.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  alloyList: PropTypes.arrayOf(PropTypes.shape({
    _id: PropTypes.string,
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  currentAlloy: PropTypes.shape({
    alloyId: PropTypes.string,
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  }).isRequired,
  getAlloysConnect: PropTypes.func.isRequired,
  deleteAlloysConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  // Ensure you use the default export name  from '../../../ducks/index.js'
  alloyList: state.alloys.user,
})

const mapDispatchToProps = {
  getAlloysConnect: getUserAlloys,
  deleteAlloysConnect: deleteUserAlloy,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserAlloys)
