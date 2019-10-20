/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * PDF report download link component. This component converts sim charts
 * to PNG image base64-encoded data URLs and only when all these images
 * are ready, this component will render PdfReport and pass the URLs to
 * PdfReport as props.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import domtoimage from 'dom-to-image'
import { PDFDownloadLink } from '@react-pdf/renderer'
import PdfReport from './PdfReport'
import { addFlashToast } from '../../../state/ducks/toast/actions'
import { logError } from '../../../api/LoggingHelper'
import { getColor } from '../../../utils/theming'

const downloadButtonStyle = {
  border: 'none',
  outline: 'none',
  textDecoration: 'none',
  width: '10rem',
  height: '2.5rem',
  padding: '0 .75rem',
  borderRadius: 6,
  transition: 'ease-in-out .4s',
  cursor: 'pointer',

  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',

  fontWeight: 600,
  letterSpacing: '0.045rem',
  boxShadow: '0 4px 6px rgba(0, 0, 0, .25)',
}

class ReportDownloadLink extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      isReady: false,
      tttUrl: '',
      cctUrl: '',
    }
  }

  render() {
    const { onError, isSimulated, addFlashToastConnect } = this.props
    const {
      hasError,
      isReady,
      tttUrl,
      cctUrl,
    } = this.state
    if (!isSimulated) return <div>No data to genereate report</div>
    if (!isReady && !hasError) {
      domtoimage.toPng(document.getElementById('ttt_chart'))
        .then((tttDataUrl) => {
          domtoimage.toPng(document.getElementById('cct_chart'))
            .then((cctDataUrl) => {
              this.setState({ cctUrl: cctDataUrl, tttUrl: tttDataUrl, isReady: true })
            })
        })
        .catch((err) => {
          addFlashToastConnect({
            message: 'Couldn\'t generate PDF report',
            options: { variant: 'error' },
          }, true)
          logError(err.toString(), err.message, 'equi.actions.getEquilibriumValues', err.stack)
          this.setState({ hasError: true })
          onError()
        })
      return <div>Your report is being prepared...</div>
    }

    if (hasError) return <div>Couldn&apos;t generate report</div>

    // only render the PDF when all the ingredients are ready
    return (
      <PDFDownloadLink
        document={<PdfReport tttUrl={tttUrl} cctUrl={cctUrl} />}
        fileName="SimCCT_report.pdf"
        style={{
          ...downloadButtonStyle,
          backgroundColor: getColor('--arc500'),
          color: getColor('--n0'),
          border: `2px solid ${getColor('--arc500')}`,
        }}
      >
        {({ loading }) => (
          loading ? 'Almost ready...' : 'Download report'
        )}
      </PDFDownloadLink>
    )
  }
}

ReportDownloadLink.propTypes = {
  // onFinish: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired,
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
