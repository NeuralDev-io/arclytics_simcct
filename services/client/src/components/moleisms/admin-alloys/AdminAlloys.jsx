import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import LoadIcon from 'react-feather/dist/icons/upload'
import EditIcon from 'react-feather/dist/icons/edit-3'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import AlloyModal from './AlloyModal'
import AlloyDeleteModal from './AlloyDeleteModal'
import {
  getGlobalAlloys,
  createGlobalAlloy,
  updateGlobalAlloy,
  deleteGlobalAlloy,
} from '../../../state/ducks/alloys/actions'
import { initSession } from '../../../state/ducks/sim/actions'
import { DEFAULT_ELEMENTS } from '../../../utils/alloys'

import styles from './AdminAlloys.module.scss'

class AdminAlloys extends Component {
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
    const { globalAlloys, getGlobalAlloysConnect } = this.props
    if (!globalAlloys || globalAlloys.length === 0) getGlobalAlloysConnect()
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
    const { createGlobalAlloyConnect } = this.props
    createGlobalAlloyConnect(alloy)
    this.handleCloseModal('add')
  }

  editAlloy = (alloy) => {
    const { updateGlobalAlloyConnect } = this.props
    const { currentAlloy } = this.state
    updateGlobalAlloyConnect({
      _id: currentAlloy._id, // eslint-disable-line
      ...alloy,
    })
    this.handleCloseModal('edit')
  }

  deleteAlloy = (alloyId) => {
    const { deleteGlobalAlloyConnect } = this.props
    deleteGlobalAlloyConnect(alloyId)
    this.handleCloseModal('delete')
  }

  handleAlloyChange = alloy => this.setState({ currentAlloy: alloy })

  handleLoadAlloy = (alloy) => {
    const {
      initSessionConnect,
      history,
    } = this.props

    // updateAlloyOptionConnect('single')
    // updateCompConnect('single', 'parent', alloy)
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
    const { globalAlloys } = this.props
    const {
      alloyId,
      currentAlloy,
      searchName,
      addModal,
      deleteModal,
      editModal,
      error,
    } = this.state

    const tableData = globalAlloys.filter(
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
              IconComponent={props => <LoadIcon {...props} />}
            >
              Load
            </Button>
            <Button
              onClick={() => this.showEditAlloy(original)}
              appearance="text"
              length="short"
              IconComponent={props => <EditIcon {...props} />}
            >
              Edit
            </Button>
            <Button
              onClick={() => this.showDeleteAlloy(original)}
              appearance="text"
              color="dangerous"
              length="short"
              IconComponent={props => <TrashIcon {...props} />}
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

AdminAlloys.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  globalAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  getGlobalAlloysConnect: PropTypes.func.isRequired,
  createGlobalAlloyConnect: PropTypes.func.isRequired,
  updateGlobalAlloyConnect: PropTypes.func.isRequired,
  deleteGlobalAlloyConnect: PropTypes.func.isRequired,
  initSessionConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
})

const mapDispatchToProps = {
  getGlobalAlloysConnect: getGlobalAlloys,
  createGlobalAlloyConnect: createGlobalAlloy,
  updateGlobalAlloyConnect: updateGlobalAlloy,
  deleteGlobalAlloyConnect: deleteGlobalAlloy,
  initSessionConnect: initSession,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminAlloys)
