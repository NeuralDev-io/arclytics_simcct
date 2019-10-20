/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * PDF report component rendered with the help of React-pdf package.
 * This component is meant to render only once when all the ingredients
 * are ready because of a bug in react-pdf.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import {
  Page,
  Text,
  View,
  Document,
  StyleSheet,
  Image,
  Font,
} from '@react-pdf/renderer'
import { getColor } from '../../../utils/theming'

// Create styles
// Font.register({
//   family: 'Quicksand',
//   src: 'https://fonts.googleapis.com/css?family=Quicksand',
// })

const styles = StyleSheet.create({
  page: {
    backgroundColor: '#fafafa',
    margin: 20,
    // fontFamily: 'Quicksand',
  },
  section: {
    padding: 10,
  },
  h4: {
    fontSize: 20,
    marginBottom: 10,
  },
  h5: {
    fontSize: 16,
    marginBottom: 8,
  },
  image: {
    width: '90%',
  },
})

// Create Document Component
class PdfReport extends React.Component {
  /**
   * This component should never update aka only render once because
   * react-pdf will crash if it tries to render while the previous rendering
   * is not finished and subsequently render 2 blank pages as default.
   * This issue was reported here
   * https://github.com/diegomura/react-pdf/issues/420
   */
  shouldComponentUpdate = () => false

  render() {
    const { tttUrl, cctUrl } = this.props
    return (
      <Document>
        <Page size="A4" style={styles.page}>
          <View style={styles.section}>
            <Text style={styles.h4}>Configurations</Text>
          </View>
        </Page>
        <Page size="A4" style={styles.page}>
          <View style={styles.section}>
            <Text style={styles.h4}>Simulation results</Text>
            <Text style={styles.h5}>TTT</Text>
            <Image src={tttUrl} style={styles.image} />
            <Text style={styles.h5}>CCT</Text>
            <Image src={cctUrl} style={styles.image} />
          </View>
        </Page>
      </Document>
    )
  }
}

export default PdfReport
