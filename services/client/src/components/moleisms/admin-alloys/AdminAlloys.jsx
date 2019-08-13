import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import PlusIcon from 'react-feather/dist/icons/plus'
import EditIcon from 'react-feather/dist/icons/edit-3'
import TrashIcon from 'react-feather/dist/icons/trash-2'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { getAlloys } from '../../../state/ducks/alloys/actions'

import styles from './AdminAlloys.module.scss'

class AdminAlloys extends Component {
  constructor(props) {
    super(props)
    this.state = {
      name: '',
    }
  }

  componentDidMount = () => {
    const { alloyList, getAlloysConnect } = this.props
    if (!alloyList || alloyList.length === 0) getAlloysConnect()
  }

  handleAlloyAction = (option) => {
    if (option.value === 'edit') prompt('edit')
  }

  render() {
    const { alloyList } = this.props
    const { name } = this.state

    console.log(alloyList, name)
    const tableData = alloyList.filter(a => a.name.includes(name))
    console.log(tableData)

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
            onClick={() => {}}
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

AdminAlloys.propTypes = {
  alloyList: PropTypes.arrayOf(PropTypes.shape({
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
  alloyList: state.alloys.list,
})

const mapDispatchToProps = {
  getAlloysConnect: getAlloys,
}

export default connect(mapStateToProps, mapDispatchToProps)(AdminAlloys)
