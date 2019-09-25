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

import styles from './FeedbackModal.module.scss'

class FeedbackModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
      backdrop: false,
      givingFeedback: props.givingFeedback || false,
      rate: -1,
      message: '',
    }
  }

  componentDidMount = () => {
    // check here if it's turn to pop up feedback modal
    this.setState({ visible: true })
  }

  handleSubmit = () => {

  }

  renderRating = () => {
    const { rate } = this.state
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
        {...buttonize(() => this.setState({ rate: point }))}
      >
        {iconArray[index]}
        <div className={styles.text}>{textArray[index]}</div>
      </div>
    ))
  }

  render() {
    const {
      visible,
      backdrop,
      givingFeedback,
      value,
      message,
    } = this.state
    return (
      <React.Fragment>
        <div
          className={`${styles.backdrop} ${backdrop ? styles.show : ''}`}
          {...buttonize(() => this.setState({ visible: false, backdrop: false }))}
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
                    onChange={val => this.setState({ message: val })}
                    value={message}
                    placeholder="Message (optional)"
                    length="stretch"
                  />
                  <div className={styles.buttonGroup}>
                    <Button
                      onClick={this.handleSubmit}
                      length="long"
                      isDisabled={value === -1}
                    >
                      Submit
                    </Button>
                    <Button
                      onClick={() => this.setState({ visible: false, backdrop: false })}
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
                    onClick={() => this.setState({ backdrop: true, givingFeedback: true })}
                    length="long"
                  >
                    Give feedback
                  </Button>
                  <Button
                    onClick={() => this.setState({ visible: false })}
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
  givingFeedback: PropTypes.bool,
}

FeedbackModal.defaultProps = {
  givingFeedback: false,
}

const mapStateToProps = (state) => ({
  
})

const mapDispatchToProps = {
  
}

export default connect(mapStateToProps, mapDispatchToProps)(FeedbackModal)
