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
import { getGlobalAlloys } from '../../../state/ducks/alloys/actions'

import styles from './AdminAlloys.module.scss'

class AdminAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      name: '',
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

  handleAddAlloy = () => {
    this.setState({ compositions: [] })
    this.handleShowModal('add')
  }

  render() {
    const { globalAlloys } = this.props
    const {
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
        Cell: (
          <div className={styles.actions}>
            <Button
              appearance="text"
              length="short"
              IconComponent={props => <EditIcon {...props} />}
            >
              Edit
            </Button>
            <Button
              onClick={() => this.handleShowModal('delete')}
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
            onClick={this.handleAddAlloy}
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
        />
        <AlloyDeleteModal
          show={deleteModal}
          onClose={() => this.handleCloseModal('delete')}
          onConfirm={() => console.log('Delete Confirmed')}
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
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
})

const mapDispatchToProps = {
  getGlobalAlloysConnect: getGlobalAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminAlloys)
