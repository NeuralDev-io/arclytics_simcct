import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Formik } from 'formik'
import XIcon from 'react-feather/dist/icons/x'
import Accordion from '../../elements/accordion'
import AccordionSection from '../../elements/accordion/AccordionSection'
import Button, { IconButton } from '../../elements/button'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'
import TextArea from '../../elements/textarea'
import { getShareUrlLink } from '../../../api/sim/SessionShareSim'

import styles from './ShareModal.module.scss'


class ShareModal extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      expandedEmail: false,
      expandedUrl: true,
      expandedExport: false,
      linkCopyDisabled: true,
      emailSubmitDisabled: true,
      shareUrlLink: '',
      copyLinkSuccess: '',
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

  onUrlLinkSubmit = () => {
    const { configurations, alloys } = this.props
    const alloyStore = {
      alloy_option: alloys.alloyOption,
      alloys: {
        parent: alloys.parent,
        weld: null,
        mix: null,
      },
    }

    const { grain_size_ASTM, grain_size_diameter, ...others } = configurations
    const validConfigs = {
      ...others,
      grain_size: grain_size_ASTM,
    }

    console.log('ShareModal:')
    console.log(configurations)
    console.log(alloyStore)

    getShareUrlLink(validConfigs, alloyStore)
      .then((res) => {
        this.setState({ shareUrlLink: res.link, linkCopyDisabled: false })
      })
  }

  copyToClipboard = (e) => {
    // TODO(andrew@neuraldev.io): Check if this works for other browsers.
    const { shareUrlLink } = this.state
    navigator.clipboard.writeText(shareUrlLink).then(() => {
      this.setState({ copyLinkSuccess: 'Copied!' })
    })
  }

  render() {
    const { show, onClose } = this.props
    const {
      expandedEmail,
      expandedUrl,
      expandedExport,
      linkCopyDisabled,
      emailSubmitDisabled,
      shareUrlLink,
      copyLinkSuccess,
    } = this.state

    return (
      <Modal
        show={show}
        className={styles.modal}
        onClose={onClose}
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
            {/* Email */}
            <AccordionSection
              title="By email"
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
                          <TextArea
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
            {/* Link */}
            <AccordionSection
              title="By URL link"
              id="url"
              expanded={expandedUrl}
              onToggle={() => this.toggleSection('Url')}
            >
              <TextField
                type="text"
                name="urlLink"
                placeholder={linkCopyDisabled ? 'Generate a URL link to copy' : 'URL Link'}
                length="stretch"
                value={shareUrlLink}
                ref={textfield => this.textField = textfield}
                isDisabled
              />

              <div className={styles.linkButtonContainer}>
                <Button
                  onClick={this.onUrlLinkSubmit}
                  name="generateLinkSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                >
                  GENERATE
                </Button>
                <Button
                  onClick={e => this.copyToClipboard(e)}
                  name="copyLinkSubmit"
                  type="button"
                  appearance="outline"
                  length="long"
                  isDisabled={linkCopyDisabled}
                >
                  COPY LINK
                </Button>
                <span>{copyLinkSuccess}</span>
              </div>
            </AccordionSection>
            {/* Export */}
            <AccordionSection
              title="By exporting to file"
              id="export"
              expanded={expandedExport}
              onToggle={() => this.toggleSection('Export')}
            >
              <TextField
                type="text"
                name="filename"
                onChange={() => console.log('Export typed')}
                placeholder="File name"
                length="stretch"
              />

              <div className={styles.exportButtonContainer}>
                <Button
                  onClick={() => console.log('Export Link')}
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
}

export default ShareModal
