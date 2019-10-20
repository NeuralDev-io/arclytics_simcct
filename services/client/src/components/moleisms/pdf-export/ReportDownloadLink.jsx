import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import domtoimage from 'dom-to-image'
import PdfReport from './PdfReport'
import { addFlashToast } from '../../../state/ducks/toast/actions'
import { logError } from '../../../api/LoggingHelper'

class ReportDownloadLink extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isReady: false,
      tttUrl: '',
      cctUrl: '',
    }
  }

  render() {
    const { isSimulated, addFlashToastConnect } = this.props
    const { isReady, tttUrl, cctUrl } = this.state
    if (!isSimulated) return <div>Nothing</div>
    if (!isReady) {
      domtoimage.toPng(document.getElementById('ttt_chart'))
        .then((tttDataUrl) => {
          this.setState({ tttUrl: tttDataUrl })
          domtoimage.toPng(document.getElementById('cct_chart'))
            .then((cctDataUrl) => {
              this.setState({ cctUrl: cctDataUrl, isReady: true })
            })
        })
        .catch((err) => {
          addFlashToastConnect({
            message: 'Couldn\'t generate PDF report',
            options: { variant: 'error' },
          }, true)
          logError(err.toString(), err.message, 'equi.actions.getEquilibriumValues', err.stack)
        })
      return <div>Nothing</div>
    }

    // only render the PDF when all the ingredients are ready
    return (
      <PdfReport tttUrl={tttUrl} cctUrl={cctUrl} />
    )
  }
}

ReportDownloadLink.propTypes = {
  // given by redux connect()
  isSimulated: PropTypes.bool.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => ({
  isSimulated: state.sim.isSimulated,
})

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(ReportDownloadLink)
