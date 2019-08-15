import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import AlloyModal from './AlloyModal'
import AlloyDeleteModal from './AlloyDeleteModal'
import {
  getGlobalAlloys,
  createGlobalAlloys,
  updateGlobalAlloys,
  deleteGlobalAlloys,
} from '../../../state/ducks/alloys/actions'

import styles from './AdminAlloys.module.scss'

class AdminAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      name: '',
      alloyId: '',
      compositions: [],
      addModal: false,
      deleteModal: false,
    }
  }

  componentDidMount = () => {
    const { globalAlloys, getGlobalAlloysConnect } = this.props
    if (!globalAlloys || globalAlloys.length === 0) getGlobalAlloysConnect()
  }

  handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  showAddAlloy = () => {
    this.setState({ compositions: [] })
    this.handleShowModal('add')
  }

  showDeleteAlloy = (alloy) => {
    this.setState({ alloyId: alloy._id }) // eslint-disable-line
    this.handleShowModal('delete')
  }

  addAlloy = (alloy) => {
    // const { createGlobalAlloysConnect } = this.props
    // createGlobalAlloysConnect(alloy)
    console.log(alloy)
  }

  deleteAlloy = (alloyId) => {
    // const { deleteGlobalAlloysConnect } = this.props
    // deleteGlobalAlloysConnect(alloyId)
    console.log('Delete alloy: ', alloyId)
    // this.handleCloseModal('delete')
  }

  render() {
    const { globalAlloys } = this.props
    const {
      alloyId,
      name,
      compositions,
      addModal,
      deleteModal,
    } = this.state

    const tableData = globalAlloys.filter(a => a.name.includes(name))

    const columns = [
      {
        Header: 'Alloy name',
        accessor: 'name',
      },
      {
        Header: '',
        Cell: ({ original }) => (
          <div className={styles.actions}>
            <Button
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
              IconComponent={props => <TrashIcon {...props} />}
            >
              Delete
            </Button>
          </div>
        ),
        width: 210,
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
              name="name"
              placeholder="Alloy name"
              value={name}
              onChange={value => this.setState({ name: value })}
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
          compositions={compositions}
          show={addModal}
          onClose={() => this.handleCloseModal('add')}
          onSave={alloy => this.addAlloy(alloy)}
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
  globalAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  getGlobalAlloysConnect: PropTypes.func.isRequired,
  createGlobalAlloysConnect: PropTypes.func.isRequired,
  updateGlobalAlloysConnect: PropTypes.func.isRequired,
  deleteGlobalAlloysConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
})

const mapDispatchToProps = {
  getGlobalAlloysConnect: getGlobalAlloys,
  createGlobalAlloysConnect: createGlobalAlloys,
  updateGlobalAlloysConnect: updateGlobalAlloys,
  deleteGlobalAlloysConnect: deleteGlobalAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminAlloys)
