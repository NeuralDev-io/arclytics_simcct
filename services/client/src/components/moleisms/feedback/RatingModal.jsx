import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { ReactComponent as Excellent } from '../../../assets/icons/feedback/excellent.svg'
import { ReactComponent as Good } from '../../../assets/icons/feedback/good.svg'
import { ReactComponent as Okay } from '../../../assets/icons/feedback/okay.svg'
import { ReactComponent as Bad } from '../../../assets/icons/feedback/bad.svg'
import { ReactComponent as Terrible } from '../../../assets/icons/feedback/terrible.svg'
import { ToastModal } from '../../elements/modal'
import { buttonize } from '../../../utils/accessibility'
import {
  updateFeedback,
  closeFeedback,
  submitRating,
} from '../../../state/ducks/feedback/actions'

import styles from './RatingModal.module.scss'

class RatingModal extends Component {
  componentDidMount = () => {
    const { updateFeedbackConnect } = this.props
    const simCount = localStorage.getItem('simCount')
    if (simCount !== undefined) {
      // check if it's turn to pop up feedback modal
      const countToShow = ['2', '4', '9', '15', '26']
      if (countToShow.includes(simCount) && localStorage.getItem('gotFeedback') !== 'true') {
        this.timer = setTimeout(() => {
          const { feedback: { feedbackVisible } } = this.props
          if (!feedbackVisible) {
            updateFeedbackConnect({ ratingVisible: true, givingFeedback: false })
          }
        }, 5000)
      }
    }
  }

  componentWillUnmount = () => {
    if (this.timer) {
      clearTimeout(this.timer)
      this.timer = 0
    }
  }

  renderRating = () => {
    const { feedback: { rate }, submitRatingConnect } = this.props
    const iconArray = [
      <Terrible key={1} className={styles.ratingIcon} />,
      <Bad key={2} className={styles.ratingIcon} />,
      <Okay key={3} className={styles.ratingIcon} />,
      <Good key={4} className={styles.ratingIcon} />,
      <Excellent key={5} className={styles.ratingIcon} />,
    ]
    // const textArray = ['Terrible', 'Bad', 'Okay', 'Good', 'Excellent']

    return [1, 2, 3, 4, 5].map((point, index) => (
      <div
        key={point}
        className={`${styles.individualRate} ${styles[`rate${point}`]} ${rate === point ? styles.active : ''}`}
        {...buttonize(() => submitRatingConnect(point))}
      >
        {iconArray[index]}
        {/* <div className={styles.text}>{textArray[index]}</div> */}
      </div>
    ))
  }

  render() {
    const {
      feedback: {
        ratingVisible,
      },
      closeFeedbackConnect,
    } = this.props

    return (
      <ToastModal
        show={ratingVisible}
        withCloseIcon
        onClose={closeFeedbackConnect}
        className={{ container: styles.container, modal: styles.modal }}
      >
        <form className={styles.getting}>
          <h6>How&apos;s your experience with us so far?</h6>
          <div className={styles.rating}>
            {this.renderRating()}
          </div>
        </form>
      </ToastModal>
    )
  }
}

RatingModal.propTypes = {
  // given by connect()
  feedback: PropTypes.shape({
    feedbackVisible: PropTypes.bool,
    ratingVisible: PropTypes.bool,
    rate: PropTypes.number,
  }).isRequired,
  updateFeedbackConnect: PropTypes.func.isRequired,
  closeFeedbackConnect: PropTypes.func.isRequired,
  submitRatingConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedback: state.feedback,
})

const mapDispatchToProps = {
  updateFeedbackConnect: updateFeedback,
  closeFeedbackConnect: closeFeedback,
  submitRatingConnect: submitRating,
}

export default connect(mapStateToProps, mapDispatchToProps)(RatingModal)
