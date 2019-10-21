/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User alloys display
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus } from '@fortawesome/pro-light-svg-icons/faPlus'
import { faUpload } from '@fortawesome/pro-light-svg-icons/faUpload'
import { faEdit } from '@fortawesome/pro-light-svg-icons/faEdit'
import { faTrashAlt } from '@fortawesome/pro-light-svg-icons/faTrashAlt'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import AlloyModal from './AlloyModal'
import AlloyDeleteModal from './AlloyDeleteModal'
import {
  getUserAlloys,
  createUserAlloy,
  updateUserAlloy,
  deleteUserAlloy,
} from '../../../state/ducks/alloys/actions'
import { initSession } from '../../../state/ducks/sim/actions'
import { DEFAULT_ELEMENTS } from '../../../utils/alloys'

import styles from './UserAlloys.module.scss'

class UserAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      alloyId: '',
      searchName: '',
      currentAlloy: {
        _id: '',
        compositions: [],
        name: '',
      },
      addModal: false,
      deleteModal: false,
      editModal: false,
    }
  }

  componentDidMount = () => {
    const { userAlloys = [], dataFetched = false, getUserAlloysConnect } = this.props
    if (!userAlloys || userAlloys.length === 0 || !dataFetched) getUserAlloysConnect()
  }

  handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  showAddAlloy = () => {
    const compositions = DEFAULT_ELEMENTS.map(sym => ({ symbol: sym, weight: 0 }))
    this.setState({
      currentAlloy: {
        _id: '',
        compositions,
        name: '',
      },
    })
    this.handleShowModal('add')
  }

  showDeleteAlloy = (alloy) => {
    this.setState({ alloyId: alloy._id }) // eslint-disable-line
    this.handleShowModal('delete')
  }

  showEditAlloy = (alloy) => {
    this.setState({ currentAlloy: alloy })
    this.handleShowModal('edit')
  }

  addAlloy = (alloy) => {
    const { createUserAlloyConnect } = this.props
    createUserAlloyConnect(alloy)
    this.handleCloseModal('add')
  }

  editAlloy = (alloy) => {
    const { updateUserAlloyConnect } = this.props
    const { currentAlloy } = this.state
    updateUserAlloyConnect({
      _id: currentAlloy._id, // eslint-disable-line
      ...alloy,
    })
    this.handleCloseModal('edit')
  }

  deleteAlloy = (alloyId) => {
    const { deleteUserAlloyConnect } = this.props
    deleteUserAlloyConnect(alloyId)
    this.handleCloseModal('delete')
  }

  handleAlloyChange = alloy => this.setState({ currentAlloy: alloy })

  handleLoadAlloy = alloy => {
    const {
      initSessionConnect,
      history,
    } = this.props

    initSessionConnect('single', 'parent', alloy)
    history.push('/')
  }

  generateColumns = () => DEFAULT_ELEMENTS.map(element => ({
    Header: element,
    id: element,
    accessor: 'compositions',
    Cell: ({ value }) => {
      const idx = value.findIndex(elem => elem.symbol === element)
      return value[idx].weight
    },
    width: 65,
    sortMethod: (a, b) => {
      const idxA = a.findIndex(elem => elem.symbol === element)
      const idxB = b.findIndex(elem => elem.symbol === element)
      return a[idxA].weight > b[idxB].weight ? 1 : -1
    },
  }))

  render() {
    const { dataFetched, dataLoading } = this.props
    let { userAlloys } = this.props
    if (!dataFetched) userAlloys = []

    const {
      alloyId,
      currentAlloy,
      searchName,
      addModal,
      deleteModal,
      editModal,
    } = this.state

    const tableData = userAlloys.filter(
      a => a.name.toLowerCase().includes(searchName.toLowerCase()),
    )

    const columns = [
      {
        Header: 'Alloy name',
        accessor: 'name',
      },
      ...this.generateColumns(),
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
              onClick={() => this.handleLoadAlloy(original)}
              appearance="text"
              length="short"
              IconComponent={props => <FontAwesomeIcon icon={faUpload} {...props} />}
            >
              Load
            </Button>
            <Button
              onClick={() => this.showEditAlloy(original)}
              appearance="text"
              length="short"
              IconComponent={props => <FontAwesomeIcon icon={faEdit}{...props} />}
            >
              Edit
            </Button>
            <Button
              onClick={() => this.showDeleteAlloy(original)}
              appearance="text"
              color="dangerous"
              length="short"
              IconComponent={props => <FontAwesomeIcon icon={faTrashAlt} {...props} />}
            >
              Delete
            </Button>
          </div>
        ),
        width: 260,
      },
    ]

    return (
      <div className={styles.container}>
        <h3>Alloy database</h3>
        <div className={styles.tools}>
          <div className="input-row">
            <span>Search</span>
            <TextField
              type="text"
              length="long"
              name="searchName"
              placeholder="Alloy name"
              value={searchName}
              onChange={value => this.setState({ searchName: value })}
            />
          </div>
          <Button
            appearance="outline"
            onClick={this.showAddAlloy}
            IconComponent={props => <FontAwesomeIcon icon={faPlus} {...props} />}
            length="short"
          >
            Add
          </Button>
        </div>
        <Table
          className="-highlight"
          data={tableData}
          columns={columns}
          loading={dataLoading}
          pageSize={tableData.length > 10 ? 10 : tableData.length}
          showPageSizeOptions={false}
          showPagination={tableData.length !== 0}
          resizable={false}
          condensed
        />
        <AlloyModal
          alloy={currentAlloy}
          onChange={this.handleAlloyChange}
          show={addModal}
          onClose={() => this.handleCloseModal('add')}
          onSave={alloy => this.addAlloy(alloy)}
        />
        <AlloyModal
          alloy={currentAlloy}
          onChange={this.handleAlloyChange}
          show={editModal}
          onClose={() => this.handleCloseModal('edit')}
          onSave={(alloy => this.editAlloy(alloy))}
        />
        <AlloyDeleteModal
          alloyId={alloyId}
          show={deleteModal}
          onClose={() => this.handleCloseModal('delete')}
          onConfirm={id => this.deleteAlloy(id)}
        />
      </div>
    )
  }
}

UserAlloys.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  userAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  dataLoading: PropTypes.bool.isRequired,
  dataFetched: PropTypes.bool.isRequired,
  getUserAlloysConnect: PropTypes.func.isRequired,
  createUserAlloyConnect: PropTypes.func.isRequired,
  updateUserAlloyConnect: PropTypes.func.isRequired,
  deleteUserAlloyConnect: PropTypes.func.isRequired,
  initSessionConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  userAlloys: state.alloys.user.data,
  dataLoading: state.alloys.user.isLoading,
  dataFetched: state.alloys.user.isFetched,
})

const mapDispatchToProps = {
  getUserAlloysConnect: getUserAlloys,
  createUserAlloyConnect: createUserAlloy,
  updateUserAlloyConnect: updateUserAlloy,
  deleteUserAlloyConnect: deleteUserAlloy,
  initSessionConnect: initSession,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserAlloys)
