/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * A custom Pagination that handles with Server Side Pagination control.
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */
/* eslint-disable no-unused-vars */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronLeft } from '@fortawesome/pro-light-svg-icons/faChevronLeft'
import { faChevronRight } from '@fortawesome/pro-light-svg-icons/faChevronRight'
import Button from '../button'

import styles from './Pagination.module.scss'

class ServerSidePagination extends Component {
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
    const totalPages = (pages === 1) ? 1 : pages + 1

    return (
      <div className={styles.pagination}>
        <div className={styles.pageNum}>
          <span className="text--sub2">
            Page {activePage} of {totalPages} {/* eslint-disable-line */}
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
          className={`${styles.button} ${activePage === totalPages && styles.disabled}`}
          onClick={() => {
            if (activePage === totalPages) return
            this.changePage(activePage + 1)
          }}
          isDisabled={activePage === totalPages}
          appearance="text"
        >
          <FontAwesomeIcon icon={faChevronRight} className={styles.icon} />
        </Button>
      </div>
    )
  }
}

ServerSidePagination.propTypes = {
  pages: PropTypes.number.isRequired,
  page: PropTypes.number.isRequired,
  pageSize: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  data: PropTypes.array.isRequired, // eslint-disable-line
}

export default ServerSidePagination
