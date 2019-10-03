import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import UndoIcon from 'react-feather/dist/icons/skip-back'
import RedoIcon from 'react-feather/dist/icons/skip-forward'
import MinusIcon from 'react-feather/dist/icons/minus'
import { AttachModal } from '../../elements/modal'
import { IconButton } from '../../elements/button'
import { timeTravelBack, timeTravelNext, timeTravelTo } from '../../../state/ducks/timeMachine/actions'
import { dangerouslyGetDateTimeString } from '../../../utils/datetime'
import { buttonize } from '../../../utils/accessibility'

import styles from './TimeTravelButtons.module.scss'

export class TimeTravelButtons extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showHistory: false,
    }
  }

  handleCloseHistory = () => this.setState({ showHistory: false })

  handleShowHistory = () => this.setState({ showHistory: true })

  handleTravelTo = (index) => {
    const { timeTravelToConnect } = this.props
    timeTravelToConnect(index)
    this.handleCloseHistory()
  }

  renderHistory = () => {
    const { timeMachine } = this.props
    return timeMachine.data.map((historyPoint, index) => (
      <div
        key={historyPoint.timestamp}
        className={styles.historyItem}
        {...buttonize(() => this.handleTravelTo(index))}
      >
        <span>{dangerouslyGetDateTimeString(historyPoint.timestamp)}</span>
      </div>
    ))
  }

  render() {
    const {
      timeTravelBackConnect,
      timeTravelNextConnect,
      timeMachine,
    } = this.props
    const { showHistory } = this.state

    return (
      <div className={styles.timeMachine}>
        <IconButton
          onClick={timeTravelBackConnect}
          Icon={props => <UndoIcon {...props} />}
          isDisabled={
            timeMachine.data.length === 0
            || timeMachine.current === 0
          }
          className={{
            button: `${styles.timeButton}
              ${(timeMachine.data.length === 0 || timeMachine.current === 0) ? styles.disabled : ''}`,
            icon: styles.timeIcon,
          }}
          withTooltip
          tooltipText="Previous"
          tooltipPosition="bottom"
        />
        <AttachModal
          visible={showHistory}
          handleClose={this.handleCloseHistory}
          handleShow={this.handleShowHistory}
          position="bottomLeft"
          overlap={false}
        >
          <IconButton
            onClick={() => {}}
            Icon={props => <MinusIcon {...props} />}
            isDisabled={timeMachine.data.length === 0}
            className={{
              button: `${styles.timeButton}
                ${(timeMachine.data.length === 0) ? styles.disabled : ''}`,
              icon: styles.timeIcon,
            }}
            withTooltip
            tooltipText="History"
            tooltipPosition="bottom"
          />
          <div className={styles.history}>
            {this.renderHistory()}
          </div>
        </AttachModal>
        <IconButton
          onClick={timeTravelNextConnect}
          Icon={props => <RedoIcon {...props} />}
          isDisabled={
            timeMachine.data.length === 0
            || timeMachine.current === timeMachine.data.length - 1
          }
          className={{
            button: `${styles.timeButton}
              ${(timeMachine.data.length === 0 || timeMachine.current === timeMachine.data.length - 1) ? styles.disabled : ''}`,
            icon: styles.timeIcon,
          }}
          withTooltip
          tooltipText="Next"
          tooltipPosition="bottom"
        />
      </div>
    )
  }
}

TimeTravelButtons.propTypes = {
  timeTravelBackConnect: PropTypes.func.isRequired,
  timeTravelNextConnect: PropTypes.func.isRequired,
  timeTravelToConnect: PropTypes.func.isRequired,
  timeMachine: PropTypes.shape({
    data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
    current: PropTypes.number,
  }).isRequired,
}

const mapStateToProps = (state) => ({
  timeMachine: state.timeMachine,
})

const mapDispatchToProps = {
  timeTravelBackConnect: timeTravelBack,
  timeTravelNextConnect: timeTravelNext,
  timeTravelToConnect: timeTravelTo,
}

export default connect(mapStateToProps, mapDispatchToProps)(TimeTravelButtons)
