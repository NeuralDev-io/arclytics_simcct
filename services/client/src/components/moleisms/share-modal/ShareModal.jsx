/* eslint-disable camelcase */
/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This is a wrapper component around the `Modal` component to add an `Accordion`
 * component with `AccordionSection` as the sections of the Share modal. The
 * component allows users to share the configurations and alloy store from the
 * user to someone else either via email, URL link, or file.
 *
 * @version 0.3.0
 * @author Dalton Le and Andrew Che
 */
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import XIcon from 'react-feather/dist/icons/x'
import Accordion from '../../elements/accordion'
import AccordionSection from '../../elements/accordion/AccordionSection'
import Button, { IconButton } from '../../elements/button'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'
import TextFieldEmail from '../../elements/textfieldemail'
import TextArea from '../../elements/textarea'
import { getShareUrlLink, sendShareEmail } from '../../../api/sim/SessionShareSim'

import styles from './ShareModal.module.scss'


class ShareModal extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      expandedEmail: true,
      expandedUrl: true,
      expandedExport: false,
      linkCopyDisabled: true,
      shareUrlLink: '',
      copyLinkSuccess: '',
      emails: [],
    }
  }

  toggleSection = (type) => {
    /** Just toggles the `AccordionSection` to open the section and its content. */
    if (type === 'Email') this.setState(prevState => ({ expandedEmail: !prevState.expandedEmail }))
    if (type === 'Url') this.setState(prevState => ({ expandedUrl: !prevState.expandedUrl }))
    if (type === 'Export') this.setState(prevState => ({ expandedExport: !prevState.expandedExport }))
  }

  cleanConfigurations = (configurations) => {
    /**
     * A helper function to remove the `grain_size_ASTM` and `grain_size_diameter`
     * from the `configurations` prop passed from the parent component. The `users`
     * server always expects to use and store the ASTM version so we put it back in
     * but we ensure we use the right request body key in the API request.
     */
    const { grain_size_ASTM, grain_size_diameter, ...others } = configurations
    return {
      ...others,
      grain_size: grain_size_ASTM,
    }
  }

  cleanAlloyStore = alloys => ({
    /**
     * A helper function just to convert an `alloys` prop to the Alloy Store that
     * the `users` server expects in an API request.
     */
    alloy_option: alloys.alloyOption,
    alloys: {
      parent: alloys.parent,
      weld: null,
      mix: null,
    },
  })

  onUrlLinkSubmit = () => {
    /**
     * The callback function for the generate button which makes the API call
     * and updates the state of `shareUrlLink` if the promise successfully returns
     * the response from the `users` server that we expect.
     */
    const { configurations, alloys } = this.props
    const alloyStore = this.cleanAlloyStore(alloys)
    const validConfigs = this.cleanConfigurations(configurations)

    // getShareUrlLink() returns a Promise and we must catch all errors.
    getShareUrlLink(validConfigs, alloyStore)
      .then((res) => {
        this.setState({ shareUrlLink: res.link, linkCopyDisabled: false })
      })
      .catch(err => console.log(err))
  }

  copyToClipboard = () => {
    /**
     * Callback function to allow the Copy button to copy the `shareUrlLink`
     * in the state to the users clipboard. The state value is updated after
     * the API call is made to the `users` server to generate a URL share link.
     * */
    // TODO(andrew@neuraldev.io): Check if this works for other browsers but it
    //  definitely works for Chrome.
    const { shareUrlLink } = this.state
    navigator.clipboard.writeText(shareUrlLink).then(() => {
      this.setState({ copyLinkSuccess: 'Copied!' })
    })
  }

  render() {
    const {
      show,
      onClose,
      configurations,
      alloys,
    } = this.props

    const {
      expandedEmail,
      expandedUrl,
      expandedExport,
      linkCopyDisabled,
      shareUrlLink,
      copyLinkSuccess,
      emails,
    } = this.state

    const validConfigs = this.cleanConfigurations(configurations)
    const alloyStore = this.cleanAlloyStore(alloys)

    return (
      <Modal
        show={show}
        className={styles.modal}
        onClose={onClose}
      >
        <header>
          <h4>Share</h4>
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
                // validate={ need to set a validate method in ValidationHelper.js}
                onSubmit={(values, { setSubmitting, setErrors }) => {
                  setSubmitting(true)
                  // We send off to the API which returns a promise
                  sendShareEmail(
                    values.email, values.message, validConfigs, alloyStore,
                  ).then((data) => {
                    console.log(data)
                    setSubmitting(false)
                  }).catch(() => {
                    // If response is unsuccessful
                    setErrors({
                      email: 'Invalid email',
                    })
                    // if it fails, we need to disable the button again.
                    setSubmitting(false)
                  })
                }}
              >
                {({
                  values,
                  errors,
                  touched,
                  onEmailSubmit,
                  setFieldValue,
                }) => (
                  // This is the form fields below
                  <form onSubmit={onEmailSubmit}>
                    <div>
                      <div className={styles.email}>
                        <TextFieldEmail
                          type="email"
                          name="email"
                          onChange={e => setFieldValue('email', e)}
                          value={''}
                          placeholder="Emails (separate with commas)"
                          length="stretch"
                        />
                        <h6 className={styles.errors}>
                          {errors.email && touched.email && errors.email}
                        </h6>
                      </div>

                      <div className={styles.message}>
                        {/* TODO(andrew@neuraldev.io): We need to validate HTML. */}
                        <TextArea
                          name="message"
                          onChange={e => setFieldValue('message', e)}
                          value={values.message}
                          placeholder="Message (optional)"
                          length="stretch"
                        />
                      </div>
                    </div>
                    <div className={styles.emailButtonContainer}>
                      <Button
                        onClick={() => console.log('Email Link')}
                        name="emailSubmit"
                        type="button"
                        appearance="outline"
                        length="long"
                        isDisabled={!(emails === undefined || emails === 0)}
                      >
                        SEND
                      </Button>
                    </div>
                  </form>
                )}
              </Formik>
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
                  onClick={this.copyToClipboard}
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

const textFieldType = PropTypes.oneOfType([
  PropTypes.string,
  PropTypes.number,
])

ShareModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  configurations: PropTypes.shape({
    method: PropTypes.string,
    grain_size_ASTM: textFieldType,
    grain_size_diameter: textFieldType,
    nucleation_start: textFieldType,
    nucleation_finish: textFieldType,
    auto_calculate_bs: PropTypes.bool,
    auto_calculate_ms: PropTypes.bool,
    ms_temp: textFieldType,
    ms_rate_param: textFieldType,
    bs_temp: textFieldType,
    auto_calculate_ae: PropTypes.bool,
    ae1_temp: textFieldType,
    ae3_temp: textFieldType,
    start_temp: textFieldType,
    cct_cooling_rate: textFieldType,
  }).isRequired,
  alloys: PropTypes.shape({
    alloyOption: PropTypes.string,
    parent: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: textFieldType,
      })),
    }),
    weld: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: textFieldType,
      })),
    }),
    mix: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: textFieldType,
    })),
    dilution: textFieldType,
  }).isRequired,
}

const mapStateToProps = state => ({
  alloys: state.sim.alloys,
  configurations: state.sim.configurations,
})

export default connect(mapStateToProps, {})(ShareModal)
