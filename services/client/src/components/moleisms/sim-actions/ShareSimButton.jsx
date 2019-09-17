import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Share2Icon from 'react-feather/dist/icons/share-2'
import Button from '../../elements/button'
import { AttachModal } from '../../elements/modal'
import Accordion from '../../elements/accordion'
import AccordionSection from '../../elements/accordion/AccordionSection'
import TextField, { TextFieldEmail } from '../../elements/textfield'
import TextArea from '../../elements/textarea'
import { getShareUrlLink, sendShareEmail } from '../../../api/sim/SessionShareSim'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './ShareSimButton.module.scss'

class ShareSimButton extends Component {
  constructor(props) {
    super(props)
    this.state = {
      linkCopyDisabled: true,
      shareUrlLink: '',
      copyLinkSuccess: '',
      emails: [],
      currentEmail: '',
      emailError: '',
      message: '',
      visible: false,
    }
  }

  handleEmailChanged = (email, error) => {
    if (error !== undefined) {
      this.setState({ emailError: error })
      return
    }
    this.setState({ currentEmail: email })
  }

  handleEmailAdded = (emails) => {
    this.setState((state) => {
      const newEmails = [...state.emails]
      emails.forEach(email => newEmails.push(email))
      return { emails: newEmails, currentEmail: '' }
    })
  }

  handleEmailRemoved = (email) => {
    this.setState(state => ({
      emails: state.emails.filter(em => em !== email),
    }))
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

  cleanResults = ({ USER, TTT, CCT }) => ({
    USER, TTT, CCT,
  })

  onUrlLinkSubmit = () => {
    /**
     * The callback function for the generate button which makes the API call
     * and updates the state of `shareUrlLink` if the promise successfully returns
     * the response from the `users` server that we expect.
     */
    const { configurations, alloys, results } = this.props
    const alloyStore = this.cleanAlloyStore(alloys)
    const validConfigs = this.cleanConfigurations(configurations)
    const simResults = this.cleanResults(results)

    // getShareUrlLink() returns a Promise and we must catch all errors.
    getShareUrlLink(validConfigs, alloyStore, simResults)
      .then((res) => {
        this.setState({ shareUrlLink: res.link, linkCopyDisabled: false })
      })
      .catch(err => console.log(err))
  }

  onEmailSubmit = () => {
    const { addFlashToastConnect } = this.props
    /**
     * The callback function for the generate button which makes the API call
     * and updates the state of `shareUrlLink` if the promise successfully returns
     * the response from the `users` server that we expect.
     */
    const { configurations, alloys, results } = this.props
    const { emails, message } = this.state

    const alloyStore = this.cleanAlloyStore(alloys)
    const validConfigs = this.cleanConfigurations(configurations)
    const simResults = this.cleanResults(results)

    sendShareEmail(
      emails, message, validConfigs, alloyStore, simResults,
    ).then(() => {
      addFlashToastConnect({
        message: 'Simulation shared successfully',
        options: { variant: 'success' },
      }, true)
      setTimeout(this.handleCloseModal, 500)
    }).catch(() => {
      addFlashToastConnect({
        message: 'Something went wrong',
        options: { variant: 'error' },
      }, true)
    })
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

  handleShowModal = () => this.setState({ visible: true })

  handleCloseModal = () => this.setState({ visible: false })

  render() {
    const {
      isSimulated,
      isAuthenticated,
    } = this.props

    const {
      linkCopyDisabled,
      shareUrlLink,
      copyLinkSuccess,
      emails,
      currentEmail,
      emailError,
      message,
      visible,
    } = this.state

    return (
      <AttachModal
        visible={visible}
        handleClose={this.handleCloseModal}
        handleShow={this.handleShowModal}
        position="topRight"
        overlap
      >
        <Button
          appearance="text"
          type="button"
          onClick={() => {}}
          IconComponent={props => <Share2Icon {...props} />}
          isDisabled={!isSimulated || !isAuthenticated}
        >
          SHARE
        </Button>
        <div className={styles.modal}>
          <h4>Share simulation</h4>
          <Accordion defaultExpand={0}>
            {/* Email */}
            <AccordionSection
              title="By email"
              id="email"
            >
              <form onSubmit={this.onEmailSubmit}>
                <div>
                  <TextFieldEmail
                    type="email"
                    name="email"
                    onChange={this.handleEmailChanged}
                    onRemove={this.handleEmailRemoved}
                    onAdd={this.handleEmailAdded}
                    emails={emails}
                    current={currentEmail}
                    error={emailError}
                    placeholder="Emails (separate with commas)"
                    length="stretch"
                  />
                  <div className={styles.message}>
                    {/* TODO(andrew@neuraldev.io): We need to validate HTML. */}
                    <TextArea
                      name="message"
                      onChange={val => this.setState({ message: val })}
                      value={message}
                      placeholder="Message (optional)"
                      length="stretch"
                    />
                  </div>
                </div>
                <div className={styles.emailButtonContainer}>
                  <Button
                    onClick={this.onEmailSubmit}
                    name="emailSubmit"
                    type="button"
                    appearance="outline"
                    length="long"
                    isDisabled={emails === undefined || emails.length === 0}
                  >
                    SEND
                  </Button>
                </div>
              </form>
            </AccordionSection>
            {/* Link */}
            <AccordionSection
              title="By URL link"
              id="url"
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
      </AttachModal>
    )
  }
}

const textFieldType = PropTypes.oneOfType([
  PropTypes.string,
  PropTypes.number,
])

ShareSimButton.propTypes = {
  isSimulated: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
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
  }).isRequired,
  results: PropTypes.shape({}).isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  alloys: state.sim.alloys,
  configurations: state.sim.configurations,
  results: state.sim.results,
})

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(ShareSimButton)
