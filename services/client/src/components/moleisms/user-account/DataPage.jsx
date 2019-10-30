import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import styles from './DataPage.module.scss'

class DataPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div className={styles.main}>
        Data personalised.
      </div>
    )
  }
}

DataPage.propTypes = {

}

const mapStateToProps = (state) => ({
  
})

const mapDispatchToProps = {
  
}

export default connect(mapStateToProps, mapDispatchToProps)(DataPage)
