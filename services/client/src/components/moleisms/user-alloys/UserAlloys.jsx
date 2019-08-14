import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import {
  postUserAlloy,
  getUserAlloys,
  getUserAlloyDetail,
  deleteUserAlloys,
  putUserAlloy
} from '../../../state/ducks/userAlloys/actions'

import styles from './UserAlloys.module.scss'

class UserAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      name: '',
    }
  }

  componentDidMount() {
    // When the component mounts, we need to get the list of alloys with API first.
    const { alloyList, getAlloysConnect } = this.props
    if (!alloyList || alloyList.length === 0) getAlloysConnect()
  }

  handleAlloyOperation = (option) => {
    if (option === 'add') console.log('add')
    if (option === 'edit') console.log('edit')
    if (option === 'delete') console.log('delete')
  }

  render() {
    const { alloyList } = this.props
    const { name } = this.state

    // Prepare the data for the Table component
    const tableData = alloyList.filter(a => a.name.includes(name))
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
              onClick={() => this.handleAlloyOperation('edit')}
              length="short"
              IconComponent={props => <EditIcon {...props} />}
            >
              Edit
            </Button>
            <Button
              appearance="text"
              onClick={() => this.handleAlloyOperation('delete')}
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
            onClick={() => this.handleAlloyOperation('add')}
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

// Type annotate props
UserAlloys.propTypes = {
  alloyList: PropTypes.arrayOf(PropTypes.shape({
    _id: PropTypes.string,
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  })).isRequired,
  getAlloysConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  // Ensure you use the default export name  from '../../../ducks/index.js'
  alloyList: state.userAlloys.list,
})

const mapDispatchToProps = {
  getAlloysConnect: getUserAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserAlloys)
