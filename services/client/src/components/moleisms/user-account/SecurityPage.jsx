import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import styles from './SecurityPage.module.scss'

class SecurityPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div className={styles.main}>
        This is secured.
      </div>
    )
  }
}

SecurityPage.propTypes = {

}

const mapStateToProps = (state) => ({
  
})

const mapDispatchToProps = {
  
}

export default connect(mapStateToProps, mapDispatchToProps)(SecurityPage)
