/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * FeedbackModal: periodically pops up to ask for feedback
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { ReactComponent as Excellent } from '../../../assets/icons/feedback/excellent.svg'
import { ReactComponent as Good } from '../../../assets/icons/feedback/good.svg'
import { ReactComponent as Okay } from '../../../assets/icons/feedback/okay.svg'
import { ReactComponent as Bad } from '../../../assets/icons/feedback/bad.svg'
import { ReactComponent as Terrible } from '../../../assets/icons/feedback/terrible.svg'
import Button from '../../elements/button'
import Select from '../../elements/select'
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
  constructor(props) {
    super(props)
    this.state = {
      categoryOptions: [
        { label: 'Features', value: 'Features' },
        { label: 'Performance', value: 'Performance' },
        { label: 'Appearance', value: 'Appearance' },
        { label: 'Others', value: 'Others' },
      ],
    }
  }

  handleClose = () => {
    const { closeFeedbackConnect } = this.props
    localStorage.setItem('gotFeedback', true)
    closeFeedbackConnect()
  }

  handleSubmit = (e) => {
    e.preventDefault()
    const { submitFeedbackConnect } = this.props
    submitFeedbackConnect()
  }

  renderRating = () => {
    const { feedback: { rate }, updateFeedbackConnect } = this.props
    const iconArray = [
      <Terrible key={1} className={styles.ratingIcon} />,
      <Bad key={2} className={styles.ratingIcon} />,
      <Okay key={3} className={styles.ratingIcon} />,
      <Good key={4} className={styles.ratingIcon} />,
      <Excellent key={5} className={styles.ratingIcon} />,
    ]
    const textArray = ['Terrible', 'Bad', 'Okay', 'Good', 'Excellent']

    return [1, 2, 3, 4, 5].map((point, index) => (
      <div
        key={point}
        className={`${styles.individualRate} ${styles[`rate${point}`]} ${rate === point ? styles.active : ''}`}
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
        feedbackVisible,
        backdrop,
        givingFeedback,
        category,
        rate,
        message,
      },
      updateFeedbackConnect,
    } = this.props
    const { categoryOptions } = this.state

    return (
      <>
        <div
          className={`${styles.backdrop} ${backdrop ? styles.show : ''}`}
          {...buttonize(this.handleClose)}
        />
        <ToastModal
          show={feedbackVisible}
          className={{ modal: `${styles.modal} ${givingFeedback ? styles.form : ''}` }}
        >
          {
            givingFeedback
              ? (
                <form className={styles.getting}>
                  <h4>We appreaciate your feedback!</h4>
                  <p>All feedback goes to our dev team to improve the app experience.</p>
                  <h6>How&apos;s your experience with us so far? *</h6>
                  <div className={styles.rating}>
                    {this.renderRating()}
                  </div>
                  <h6>This feedback is mainly about *</h6>
                  <Select
                    name="category"
                    placeholder="Choose category"
                    options={categoryOptions}
                    value={categoryOptions[categoryOptions.findIndex(c => c.value === category)]}
                    length="stretch"
                    onChange={val => updateFeedbackConnect({ category: val.value })}
                    className={styles.select}
                    isSearchable
                  />
                  <h6>Tell us more about your experience *</h6>
                  <TextArea
                    name="message"
                    onChange={val => updateFeedbackConnect({ message: val })}
                    value={message}
                    placeholder="Message"
                    length="stretch"
                    rows={8}
                  />
                  <div className={styles.buttonGroup}>
                    <Button
                      onClick={this.handleSubmit}
                      type="submit"
                      length="long"
                      isDisabled={rate === -1 || category === '' || message === ''}
                    >
                      Submit
                    </Button>
                    <Button
                      onClick={this.handleClose}
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
                    onClick={this.handleClose}
                    appearance="text"
                  >
                    No, thanks
                  </Button>
                </div>
              )
          }
        </ToastModal>
      </>
    )
  }
}

FeedbackModal.propTypes = {
  // given by connect()
  feedback: PropTypes.shape({
    feedbackVisible: PropTypes.bool,
    backdrop: PropTypes.bool,
    givingFeedback: PropTypes.bool,
    category: PropTypes.string,
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
