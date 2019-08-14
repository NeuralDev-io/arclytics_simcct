import React, { PureComponent, useState } from 'react'
import PropTypes from 'prop-types'
import { Formik } from 'formik'
import XIcon from 'react-feather/dist/icons/x'
import { loginValidation } from '../../../utils/ValidationHelper'
import { login } from '../../../utils/AuthenticationHelper'
import Accordion from '../../elements/accordion'
import AccordionSection from '../../elements/accordion/AccordionSection'
import Button, { IconButton } from '../../elements/button'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'

import styles from './ShareModal.module.scss'


class ShareModal extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      expandedEmail: true,
      expandedUrl: true,
      expandedExport: false,
      linkCopyDisabled: true,
      emailSubmitDisabled: true,
    }
  }

  toggleSection = (type) => {
    if (type === 'Email') this.setState(prevState => ({ expandedEmail: !prevState.expandedEmail }))
    if (type === 'Url') this.setState(prevState => ({ expandedUrl: !prevState.expandedUrl }))
    if (type === 'Export') this.setState(prevState => ({ expandedExport: !prevState.expandedExport }))
  }

  onEmailSubmit = () => {
    console.log('Email Submitted')
  }

  render() {
    const { show, onClose, onConfirm } = this.props
    const {
      expandedEmail,
      expandedUrl,
      expandedExport,
      linkCopyDisabled,
      emailSubmitDisabled,
    } = this.state

    return (
      <Modal
        show={show}
        className={styles.modal}
        onClose={onClose}
        withCloseIcon
      >
        <header>
          <h3>Share</h3>
          <IconButton
            onClick={onClose}
            Icon={props => <XIcon {...props} />}
            className={styles.closeButton}
          />
        </header>
        <div>
          <Accordion>
            <AccordionSection
              title="Email"
              id="email"
              expanded={expandedEmail}
              onToggle={() => this.toggleSection('Email')}
            >
              <Formik
                initialValues={{ email: '', message: '' }}
                // validate={loginValidation}
                onSubmit={() => console.log('Form submitted')}
              >
                {({
                  values,
                  errors,
                  touched,
                  handleSubmit,
                  setFieldValue,
                  isSubmitting,
                }) => (
                  <div className={styles.formContainer}>
                    <form onSubmit={handleSubmit}>
                      <div>
                        <div className={styles.email}>
                          <TextField
                            type="email"
                            name="email"
                            onChange={e => setFieldValue('email', e)}
                            value={values.email}
                            placeholder="Email"
                            length="stretch"
                          />
                          <h6 className={styles.errors}>
                            {errors.email && touched.email && errors.email}
                          </h6>
                        </div>

                        <div className={styles.message}>
                          <TextField
                            type="text"
                            name="message"
                            // onChange={e => setFieldValue('', e)}
                            value={values.message}
                            placeholder="Message (optional)"
                            length="stretch"
                          />
                          <h6 className={styles.errors}>
                            {errors.message && touched.message && errors.message}
                          </h6>
                        </div>
                      </div>
                    </form>
                  </div>
                )}
              </Formik>
              <div className={styles.emailButtonContainer}>
                <Button
                  onClick={() => console.log('Email Link')}
                  name="emailSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                  isDisabled={emailSubmitDisabled}
                >
                  SEND
                </Button>
              </div>
            </AccordionSection>

            <AccordionSection
              title="URL Link"
              id="url"
              expanded={expandedUrl}
              onToggle={() => this.toggleSection('Url')}
            >
              <TextField
                type="text"
                name="urlLink"
                // onChange={e => setFieldValue('email', e)}
                placeholder="URL Link"
                length="stretch"
              />

              <div className={styles.linkButtonContainer}>
                <Button
                  onClick={() => console.log('Copy Link')}
                  name="generateLinkSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                >
                  GENERATE
                </Button>
                <Button
                  onClick={() => console.log('Copy Link')}
                  name="copyLinkSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                  isDisabled={linkCopyDisabled}
                >
                  COPY LINK
                </Button>
              </div>
            </AccordionSection>

            <AccordionSection
              title="Export to File"
              id="export"
              expanded={expandedExport}
              onToggle={() => this.toggleSection('Export')}
            >
              <TextField
                type="text"
                name="filename"
                // onChange={e => setFieldValue('email', e)}
                placeholder="File name"
                length="stretch"
              />

              <div className={styles.exportButtonContainer}>
                <Button
                  onClick={() => console.log('Copy Link')}
                  name="exportFileSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                >
                  EXPORT
                </Button>
              </div>
            </AccordionSection>

          </Accordion>
        </div>
      </Modal>
    )
  }
}

ShareModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default ShareModal
