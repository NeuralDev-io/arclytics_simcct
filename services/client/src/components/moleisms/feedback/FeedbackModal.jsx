import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { ReactComponent as Excellent } from '../../../assets/icons/feedback/good.svg'
import { ReactComponent as Good } from '../../../assets/icons/feedback/good.svg'
import { ReactComponent as Okay } from '../../../assets/icons/feedback/okay.svg'
import { ReactComponent as Bad } from '../../../assets/icons/feedback/bad.svg'
import { ReactComponent as Terrible } from '../../../assets/icons/feedback/bad.svg'
import Button from '../../elements/button'
import TextArea from '../../elements/textarea'
import { ToastModal } from '../../elements/modal'
import { buttonize } from '../../../utils/accessibility'
import {
  updateFeedback,
  closeFeedback,
  submitFeedback,
} from '../../../state/ducks/feedback/actions'

import styles from './FeedbackModal.module.scss'

class FeedbackModal extends Component {
  componentDidMount = () => {
    const { updateFeedbackConnect } = this.props
    // check here if it's turn to pop up feedback modal
    updateFeedbackConnect({ visible: true })
  }

  handleSubmit = () => {

  }

  renderRating = () => {
    const { feedback: { rate }, updateFeedbackConnect } = this.props
    const iconArray = [
      <Terrible key={1} className={`${styles.ratingIcon} ${styles.rate1} ${rate === 1 ? styles.active : ''}`} />,
      <Bad key={2} className={`${styles.ratingIcon} ${styles.rate2} ${rate === 2 ? styles.active : ''}`} />,
      <Okay key={3} className={`${styles.ratingIcon} ${styles.rate3} ${rate === 3 ? styles.active : ''}`} />,
      <Good key={4} className={`${styles.ratingIcon} ${styles.rate4} ${rate === 4 ? styles.active : ''}`} />,
      <Excellent key={5} className={`${styles.ratingIcon} ${styles.rate5} ${rate === 5 ? styles.active : ''}`} />,
    ]
    const textArray = ['Terrible', 'Bad', 'Okay', 'Good', 'Excellent']

    return [1, 2, 3, 4, 5].map((point, index) => (
      <div
        key={point}
        className={styles.individualRate}
        {...buttonize(() => updateFeedbackConnect({ rate: point }))}
      >
        {iconArray[index]}
        <div className={styles.text}>{textArray[index]}</div>
      </div>
    ))
  }

  render() {
    const {
      feedback: {
        visible,
        backdrop,
        givingFeedback,
        rate,
        message,
      },
      updateFeedbackConnect,
      closeFeedbackConnect,
    } = this.props
    return (
      <React.Fragment>
        <div
          className={`${styles.backdrop} ${backdrop ? styles.show : ''}`}
          {...buttonize(closeFeedbackConnect)}
        />
        <ToastModal show={visible} className={`${styles.modal} ${givingFeedback ? styles.form : ''}`}>
          {
            givingFeedback
              ? (
                <form className={styles.getting}>
                  <h4>We appreaciate your feedback!</h4>
                  <p>All feedback goes to our dev team to improve the app experience.</p>
                  <h6>How&apos;s your experience with us so far?</h6>
                  <div className={styles.rating}>
                    {this.renderRating()}
                  </div>
                  <h6>Tell us more about your experience</h6>
                  <TextArea
                    name="message"
                    onChange={val => updateFeedbackConnect({ message: val })}
                    value={message}
                    placeholder="Message (optional)"
                    length="stretch"
                  />
                  <div className={styles.buttonGroup}>
                    <Button
                      onClick={this.handleSubmit}
                      length="long"
                      isDisabled={rate === -1}
                    >
                      Submit
                    </Button>
                    <Button
                      onClick={closeFeedbackConnect}
                      length="long"
                      appearance="text"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              )
              : (
                <div className={styles.asking}>
                  <h6>Help us improve your experience.</h6>
                  <Button
                    onClick={() => updateFeedbackConnect({ backdrop: true, givingFeedback: true })}
                    length="long"
                  >
                    Give feedback
                  </Button>
                  <Button
                    onClick={() => updateFeedbackConnect({ visible: false })}
                    appearance="text"
                  >
                    No, thanks
                  </Button>
                </div>
              )
          }
        </ToastModal>
      </React.Fragment>
    )
  }
}

FeedbackModal.propTypes = {
  // given by connect()
  feedback: PropTypes.shape({
    visible: PropTypes.bool,
    backdrop: PropTypes.bool,
    givingFeedback: PropTypes.bool,
    rate: PropTypes.number,
    message: PropTypes.string,
  }).isRequired,
  updateFeedbackConnect: PropTypes.func.isRequired,
  closeFeedbackConnect: PropTypes.func.isRequired,
  submitFeedbackConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  feedback: state.feedback,
})

const mapDispatchToProps = {
  updateFeedbackConnect: updateFeedback,
  closeFeedbackConnect: closeFeedback,
  submitFeedbackConnect: submitFeedback,
}

export default connect(mapStateToProps, mapDispatchToProps)(FeedbackModal)
