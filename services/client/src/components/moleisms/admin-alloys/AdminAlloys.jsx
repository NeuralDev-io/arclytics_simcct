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
          data={alloyList}
          columns={columns}
          pageSize={alloyList.length > 10 ? 10 : alloyList.length}
          showPageSizeOptions={false}
          showPagination={alloyList.length !== 0}
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
