import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronLeft } from '@fortawesome/pro-light-svg-icons/faChevronLeft'
import { faChevronRight } from '@fortawesome/pro-light-svg-icons/faChevronRight'
import Button from '../button'

import styles from './Pagination.module.scss'

class Pagination extends Component {
  componentDidUpdate = (prevProps) => {
    const { page } = this.props
    if (prevProps.page !== page) this.changePage(page + 1)
  }

  changePage = (newPage) => {
    const { page, onPageChange } = this.props
    const activePage = page + 1

    if (newPage === activePage) {
      return
    }

    onPageChange(newPage - 1)
  }

  render() {
    const {
      page,
      pages,
      pageSize,
      data,
    } = this.props
    const activePage = page + 1
    const startRow = page * pageSize + 1
    const endRow = (page + 1) * pageSize > data.length ? data.length : (page + 1) * pageSize

    return (
      <div className={styles.pagination}>
        <div className={styles.pageNum}>
          <span className="text--sub2">
            {startRow}-{endRow} of {data.length} {/* eslint-disable-line */}
          </span>
        </div>
        <Button
          className={`${styles.button} ${activePage === 1 && styles.disabled}`}
          onClick={() => {
            if (activePage === 1) return
            this.changePage(activePage - 1)
          }}
          isDisabled={activePage === 1}
          appearance="text"
        >
          <FontAwesomeIcon icon={faChevronLeft} className={styles.icon} />
        </Button>
        <Button
          className={`${styles.button} ${activePage === pages && styles.disabled}`}
          onClick={() => {
            if (activePage === pages) return
            this.changePage(activePage + 1)
          }}
          isDisabled={activePage === pages}
          appearance="text"
        >
          <FontAwesomeIcon icon={faChevronRight} className={styles.icon} />
        </Button>
      </div>
    )
  }
}

Pagination.propTypes = {
  pages: PropTypes.number.isRequired,
  page: PropTypes.number.isRequired,
  pageSize: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  data: PropTypes.array.isRequired, // eslint-disable-line
}

export default Pagination
