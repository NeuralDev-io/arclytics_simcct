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
import PropTypes from 'prop-types'
import {
  Page,
  Text,
  View,
  Document,
  StyleSheet,
  Image,
  Font,
} from '@react-pdf/renderer'
import { ANSTOLogo, arcLogo } from './LogoData'
import { roundTo } from '../../../utils/math'

// Create styles
Font.register({
  family: 'Lato',
  fonts: [
    { src: 'http://fonts.gstatic.com/s/lato/v16/S6uyw4BMUTPHvxk6XweuBCY.ttf' },
    { src: 'http://fonts.gstatic.com/s/lato/v16/S6u9w4BMUTPHh6UVew-FGC_p9dw.ttf', fontWeight: 700 },
    { src: 'http://fonts.gstatic.com/s/lato/v16/S6u9w4BMUTPHh7USew-FGC_p9dw.ttf', fontWeight: 300 },
  ],
})

const headingStyles = {
  marginVertical: 12,
  fontWeight: 700,
  lineHeight: 1.5,
  cursor: 'text',
}

const styles = StyleSheet.create({
  page: {
    backgroundColor: '#fafafa',
    color: '#34495e',
    marginVertical: 0,
    marginHorizontal: 'auto',
    fontSize: 12,
    fontFamily: 'Lato',
    fontWeight: 400,
    lineHeight: 1.5,
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: 50,
    width: '100%',
    paddingHorizontal: 50,
    marginTop: 10,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    height: 50,
    width: '100%',
    paddingHorizontal: 50,
    marginBottom: 25,
  },
  logoANSTO: {
    // width: 50,
    height: 22,
    position: 'absolute',
    top: 15,
    right: 0,
    opacity: 0.8,
  },
  logoArc: {
    height: 22,
    position: 'absolute',
    top: 15,
    left: 0,
    opacity: 0.8,
  },
  pageContent: {
    marginTop: 50,
    marginBottom: 40,
    paddingHorizontal: 50,
  },
  h1: {
    ...headingStyles,
    fontSize: 28,
    paddingBottom: 6,
    lineHeight: 1.3,
  },
  h2: {
    ...headingStyles,
    fontSize: 25,
    lineHeight: 1.225,
    marginTop: 30,
    marginBottom: 12,
    paddingBottom: 8,
    borderBottom: '1px solid #dddddd',
  },
  h3: {
    ...headingStyles,
    fontSize: 20,
    lineHeight: 1.43,
    marginTop: 18,
    marginBottom: 12,
  },
  h4: {
    ...headingStyles,
    fontSize: 16,
  },
  h5: {
    ...headingStyles,
    fontSize: 13,
    marginBottom: 8,
  },
  h6: {
    ...headingStyles,
    fontSize: 12,
    color: '#777',
  },
  strong: {
    fontWeight: 700,
    lineHeight: 1.5,
  },
  image: {
    width: '80%',
    marginHorizontal: 'auto',
  },
  compositions: {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  compItem: {
    marginRight: 30,
    marginBottom: 8,
    width: 40,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    flexShrink: 0,
  },
  configItem: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  transform: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  transformGroup: {
    marginRight: 70,
  },
  nucleations: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  references: {
    marginBottom: 8,
  },
})

const methodOptions = {
  Li98: 'Li (98)',
  Kirkaldy83: 'Kirkaldy (83)',
}

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

  renderComp = comp => comp.map((compItem, index) => (
    <View
      // debug
      style={[
        styles.compItem,
        (() => {
          if (index === comp.length - 1) return { marginRight: 'auto' }
          return {}
        })(),
      ]}
      key={compItem.symbol}
    >
      <Text style={[styles.strong, { color: '#0076C2' }]}>{compItem.symbol}</Text>
      <Text>{compItem.weight}</Text>
    </View>
  ))

  render() {
    const {
      tttUrl,
      cctUrl,
      equiUrl,
      alloy,
      configurations,
      equi,
    } = this.props
    return (
      <Document>
        <Page size="A4" style={styles.page}>
          <View style={styles.pageContent}>
            <Text style={[styles.h1, { marginTop: 0 }]}>Arclytics SimCCT report</Text>
            <View style={[styles.configItem, { marginBottom: 16 }]}>
              <Text style={styles.strong}>Date generated:</Text>
              <Text>
                &nbsp;
                {new Date().toLocaleString()}
              </Text>
            </View>
            <View style={styles.section}>
              <Text style={[styles.h3, { marginTop: 0 }]}>Alloy</Text>
              <View style={styles.configItem}>
                <Text style={[styles.strong, { width: 60 }]}>Name</Text>
                <Text>{alloy.name}</Text>
              </View>
              <View>
                <Text style={[styles.h5, { marginTop: 0 }]}>Composition</Text>
                <View style={styles.compositions}>
                  {this.renderComp(alloy.compositions)}
                </View>
              </View>
            </View>
            <View style={styles.section}>
              <Text style={styles.h3}>Configurations</Text>
              <View style={styles.configurations}>
                <Text style={[styles.h4, { marginTop: 0 }]}>General</Text>
                <View style={styles.configItem}>
                  <Text style={[styles.strong, { width: 120 }]}>
                    CCT/TTT method
                  </Text>
                  <Text>{methodOptions[configurations.method]}</Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={[styles.strong, { width: 120 }]}>Grain size</Text>
                  <Text>
                    {configurations.grain_size_ASTM}
                    &nbsp;ASTM (diameter =&nbsp;
                    {configurations.grain_size_diameter}
                    &nbsp;&micro;m)
                  </Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={[styles.strong, { width: 120 }]}>
                    Start temperature
                  </Text>
                  <Text>
                    {configurations.start_temp}
                    &nbsp;°C
                  </Text>
                </View>
                <View style={[styles.configItem, { marginBottom: 0 }]}>
                  <Text style={[styles.strong, { width: 120 }]}>
                    CCT Cooling rate
                  </Text>
                  <Text>
                    {configurations.cct_cooling_rate}
                    &nbsp;°C/sec
                  </Text>
                </View>
                <Text style={styles.h4}>Transformation limits</Text>
                <View style={styles.transform}>
                  <View style={styles.transformGroup}>
                    <Text style={[styles.h5, { marginTop: 0 }]}>
                      Ferrite/Pearlite
                    </Text>
                    <View style={styles.configItem}>
                      <Text style={[styles.strong, { width: 40 }]}>Ae1</Text>
                      <Text>
                        {roundTo(configurations.ae1_temp, 1)}
                        &nbsp;°C
                      </Text>
                    </View>
                    <View style={styles.configItem}>
                      <Text style={[styles.strong, { width: 40 }]}>Ae3</Text>
                      <Text>
                        {roundTo(configurations.ae3_temp, 1)}
                        &nbsp;°C
                      </Text>
                    </View>
                  </View>
                  <View style={styles.transformGroup}>
                    <Text style={[styles.h5, { marginTop: 0 }]}>Bainite</Text>
                    <View style={styles.configItem}>
                      <Text style={[styles.strong, { width: 30 }]}>Bs</Text>
                      <Text>
                        {roundTo(configurations.bs_temp, 1)}
                        &nbsp;°C
                      </Text>
                    </View>
                  </View>
                  <View>
                    <Text style={[styles.h5, { marginTop: 0 }]}>Martensite</Text>
                    <View style={styles.configItem}>
                      <Text style={[styles.strong, { width: 80 }]}>Ms</Text>
                      <Text>
                        {roundTo(configurations.ms_temp, 1)}
                        &nbsp;°C
                      </Text>
                    </View>
                    <View style={styles.configItem}>
                      <Text style={[styles.strong, { width: 80 }]}>Ms rate</Text>
                      <Text>
                        {roundTo(configurations.ms_rate_param, 3)}
                        &nbsp;°C
                      </Text>
                    </View>
                  </View>
                </View>
                <Text style={styles.h4}>Nucleation parameters</Text>
                <View style={styles.nucleations}>
                  <View style={[styles.configItem, { width: 160 }]}>
                    <Text style={[styles.strong, { width: 40 }]}>Start</Text>
                    <Text>
                      {configurations.nucleation_start}
                      &nbsp;%
                    </Text>
                  </View>
                  <View style={styles.configItem}>
                    <Text style={[styles.strong, { width: 40 }]}>Finish</Text>
                    <Text>
                      {configurations.nucleation_finish}
                      &nbsp;%
                    </Text>
                  </View>
                </View>
              </View>
            </View>
          </View>
          <View style={styles.footer} fixed>
            <View style={{ width: '100%', height: 50, position: 'relative' }}>
              <Image
                src={arcLogo}
                style={styles.logoArc}
              />
              <Image
                src={ANSTOLogo}
                style={styles.logoANSTO}
              />
            </View>
          </View>
        </Page>
        <Page sise="A4" style={styles.page}>
          <View style={styles.pageContent}>
            <Text style={[styles.h3, { marginTop: 0 }]}>Ae3 Equilibrium</Text>
            <Text style={[styles.h4, { marginTop: 0 }]}>Configurations</Text>
            <View style={styles.configItem}>
              <Text style={[styles.strong, { width: 140 }]}>
                Ferrite phase fraction
              </Text>
              <Text style={[styles.strong, { width: 60, color: '#0076C2' }]}>
                Xfe
              </Text>
              <Text>{roundTo(equi.xfe, 3)}</Text>
            </View>
            <View style={styles.configItem}>
              <Text style={[styles.strong, { width: 140 }]}>Eutectic Carbon</Text>
              <Text style={[styles.strong, { width: 60, color: '#0076C2' }]}>
                Ceut
              </Text>
              <Text>
                {roundTo(equi.ceut, 3)}
                &nbsp;wt%
              </Text>
            </View>
            <View style={styles.configItem}>
              <Text style={[styles.strong, { width: 140 }]}>
                Ferrite phase fraction
              </Text>
              <Text style={[styles.strong, { width: 60, color: '#0076C2' }]}>
                Cf
              </Text>
              <Text>{roundTo(equi.cf, 3)}</Text>
            </View>
            <View>
              <Text style={styles.h4}>Visualisation</Text>
              <Image src={equiUrl} style={styles.image} />
            </View>
          </View>
          <View style={styles.footer} fixed>
            <View style={{ width: '100%', height: 50, position: 'relative' }}>
              <Image
                src={arcLogo}
                style={styles.logoArc}
              />
              <Image
                src={ANSTOLogo}
                style={styles.logoANSTO}
              />
            </View>
          </View>
        </Page>
        <Page size="A4" style={styles.page}>
          <View style={styles.pageContent}>
            <View style={styles.section}>
              <Text style={[styles.h3, { marginTop: 0 }]}>
                Simulation results
              </Text>
              <Text style={[styles.h4, { marginTop: 0 }]}>TTT</Text>
              <Image src={tttUrl} style={styles.image} />
              <Text style={styles.h4}>CCT</Text>
              <Image src={cctUrl} style={styles.image} />
            </View>
          </View>
          <View style={styles.footer} fixed>
            <View style={{ width: '100%', height: 50, position: 'relative' }}>
              <Image
                src={arcLogo}
                style={styles.logoArc}
              />
              <Image
                src={ANSTOLogo}
                style={styles.logoANSTO}
              />
            </View>
          </View>
        </Page>
        <Page size="A4" style={styles.page}>
          <View style={styles.pageContent}>
            <Text style={[styles.h3, { marginTop: 0 }]}>References</Text>
            <Text style={styles.references}>
              Kirkaldy, J.C. and D. Venugopalan. Prediction of microstructure and
              hardenability in low alloy steels. in Phase Transformations in
              Ferrous Alloys. 1983. Philadelphia, PA.
            </Text>
            <Text style={styles.references}>
              Kirkaldy, J., Diffusion-controlled phase transformations in steels.
              Theory and applications. Scandinavian journal of metallurgy, 1991.
              20(1): p. 50-61.
            </Text>
            <Text style={styles.references}>
              Li, M., Computational modeling of heat transfer and microstructure
              development in the electroslag cladding heat affected zone of low
              alloy steels. 1996.
            </Text>
            <Text style={styles.references}>
              Li, M.V., et al., A computational model for the prediction of steel
              hardenability. Metallurgical and Materials transactions B, 1998.
              29(3): p. 661-672.
            </Text>
            <Text style={styles.references}>
              Hamelin, C.J., et al., Predicting solid-state phase transformations
              during welding of ferritic steels, in Materials Science Forum. 2012.
              p. 1403-1408.
            </Text>
            <Text style={styles.references}>
              Hamelin, C.J., et al. Predicting post-weld residual stresses in
              ferritic steel weldments. in American Society of Mechanical
              Engineers, Pressure Vessels and Piping Division (Publication) PVP.
              2012.
            </Text>
            <Text style={styles.references}>
              Hamelin, C.J., et al. Accounting for phase transformations during
              welding of ferritic steels. in American Society of Mechanical
              Engineers, Pressure Vessels and Piping Division (Publication) PVP.
              2011.
            </Text>
            <Text style={styles.references}>
              Hamelin, C.J., et al., Validation of a numerical model used to
              predict phase distribution and residual stress in ferritic steel
              weldments. Acta Materialia, 2014. 75(0): p. 1-19.
            </Text>
            <Text style={styles.references}>
              Abaqus. 2018, Dassault Systèmes -SIMULIA.
            </Text>
            <Text style={styles.references}>
              Ikawa, H., H. Oshige, and S. Noi, Austenite Grain Growth of Steel in
              Weld-Heat Affected Zone. Transactions of the Japan Welding Society,
              1977. 8(2): p. 132-137.
            </Text>
            <Text style={styles.references}>
              Ikawa, H., et al., Austenite Grain Growth of Steels during Thermal
              Cycles. Transactions of the Japan Welding Society, 1977. 8(2): p.
              126-131.
            </Text>
            <Text style={styles.references}>
              Koıstinen, D. and R.J.A.M. Marbürger, A General Equation Prescribing
              Extent of Austenite- Martensite Transformation in Pure Fe-C Alloy
              and Plain Carbon Steels. 1959. 7(1): p. 59-60.
            </Text>
          </View>
          <View style={styles.footer} fixed>
            <View style={{ width: '100%', height: 50, position: 'relative' }}>
              <Image
                src={arcLogo}
                style={styles.logoArc}
              />
              <Image
                src={ANSTOLogo}
                style={styles.logoANSTO}
              />
            </View>
          </View>
        </Page>
      </Document>
    )
  }
}

const configType = PropTypes.oneOfType([
  PropTypes.string, PropTypes.number,
])

PdfReport.propTypes = {
  tttUrl: PropTypes.string.isRequired,
  cctUrl: PropTypes.string.isRequired,
  equiUrl: PropTypes.string.isRequired,
  alloy: PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: configType,
    })),
  }).isRequired,
  configurations: PropTypes.shape({
    method: configType,
    grain_size_ASTM: configType,
    grain_size_diameter: configType,
    ae1_temp: configType,
    ae3_temp: configType,
    bs_temp: configType,
    ms_temp: configType,
    ms_rate_param: configType,
    nucleation_start: configType,
    nucleation_finish: configType,
    start_temp: configType,
    cct_cooling_rate: configType,
  }).isRequired,
  equi: PropTypes.shape({
    xfe: configType,
    ceut: configType,
    cf: configType,
  }).isRequired,
}

export default PdfReport
