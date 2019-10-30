/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * About Application
 *
 * @version 1.0.0
 * @author Dalton Le, Andrew Che
 *
 * The disclaimer information for the application.
 *
 */

import React from 'react'

import styles from './Acknowledgements.module.scss'

const packages = [
  { name: 'Docker', link: '' },
  { name: 'Kubernetes', link: '' },
  { name: 'conda', link: '' },
  { name: 'Flask', link: '' },
  { name: 'gunicorn', link: '' },
  { name: 'Celery', link: '' },
  { name: 'NodeJS', link: '' },
  { name: 'React', link: '' },
  { name: 'MongoDB', link: '' },
  { name: 'Redis', link: '' },
  { name: 'Plotly', link: '' },
  { name: 'numpy', link: '' },
  { name: 'pandas', link: '' },
  { name: 'jupyter', link: '' },
  { name: 'fluentd', link: '' },
  { name: 'Elasticsearch', link: '' },
  { name: 'Kibana', link: '' },
  { name: 'Elastic APM', link: '' },
  { name: 'Marshmallow', link: '' },
  { name: 'Flask-RESTful', link: '' },
  { name: 'Swagger', link: '' },
]

class Acknowledgements extends React.PureComponent {
  renderPackageList = () => packages.map(packageItem => (
    <li key={packageItem.name} className={styles.packageItem}>
      <a
        href={packageItem.link}
        target="_blank"
        rel="noopener noreferrer"
      >
        {packageItem.name}
      </a>
    </li>
  ))

  render() {
    return (
      <div className={styles.container}>
        <h3>Acknowledgements</h3>
        <div className={styles.updateHistory}>
          <p>
            <strong>Last updated:</strong>
            &nbsp;October 20, 2019
          </p>
          &nbsp;
        </div>
        <section>
          <div className={styles.acknowledgements}>
            <p>
              This application was made with the help of the open-source
              community. Packages include:
            </p>
            <ul className={styles.packageList}>
              {this.renderPackageList()}
            </ul>
            <p>
              We would also like to acknowledge the &nbsp;
              <a
                href="https://www.uow.edu.au/southwesternsydneycampus/"
                target="_blank"
                rel="noopener noreferrer"
              >
                University of Wollongong (South Western Sydney campus)
              </a>
              &nbsp; academic and student services staff for their support.
            </p>
          </div>
        </section>

        <section className={styles.references}>
          <h4>References</h4>
          <ol className={styles.references}>
            <li value="1">
              Kirkaldy, J.C. and D. Venugopalan. Prediction of microstructure
              and hardenability in low alloy steels. in Phase Transformations in
              Ferrous Alloys. 1983. Philadelphia, PA.
            </li>
            <li value="2">
              Kirkaldy, J., Diffusion-controlled phase transformations in
              steels. Theory and applications. Scandinavian journal of
              metallurgy, 1991. 20(1): p. 50-61.
            </li>
            <li value="3">
              Li, M., Computational modeling of heat transfer and microstructure
              development in the electroslag cladding heat affected zone of low
              alloy steels. 1996.
            </li>
            <li value="4">
              Li, M.V., et al., A computational model for the prediction of
              steel hardenability. Metallurgical and Materials transactions B,
              1998. 29(3): p. 661-672.
            </li>
            <li value="5">
              Hamelin, C.J., et al., Predicting solid-state phase
              transformations during welding of ferritic steels, in Materials
              Science Forum. 2012. p. 1403-1408.
            </li>
            <li value="6">
              Hamelin, C.J., et al. Predicting post-weld residual stresses in
              ferritic steel weldments. in American Society of Mechanical
              Engineers, Pressure Vessels and Piping Division (Publication) PVP.
              2012.
            </li>
            <li value="7">
              Hamelin, C.J., et al. Accounting for phase transformations during
              welding of ferritic steels. in American Society of Mechanical
              Engineers, Pressure Vessels and Piping Division (Publication) PVP.
              2011.
            </li>
            <li value="8">
              Hamelin, C.J., et al., Validation of a numerical model used to
              predict phase distribution and residual stress in ferritic steel
              weldments. Acta Materialia, 2014. 75(0): p. 1-19.
            </li>
            <li value="9">Abaqus. 2018, Dassault Systèmes -SIMULIA.</li>
            <li value="10">
              Zener, C.J.T.A., Kinetics of the decomposition of austenite.
              1946. 167(1946): p. 550-595.
            </li>
            <li value="11">
              Hillert, M.J.J.A., The role of interfacial energy during
              solid-state phase transformations. 1957. 141: p. 757-789.
            </li>
            <li value="12">
              Scheil, E.J.A.E., Nucleation period of austenite transformation.
              1935. 12: p. 565-567.
            </li>
            <li value="13">
              Watt, D., et al., An algorithm for modelling microstructural
              development in weld heataffected zones (part A) reaction kinetics.
              Acta Metallurgica, 1988. 36(11): p. 3029-3035.
            </li>
            <li value="14">
              Gorni, A.A.J.S.V., Brazil, Steel forming and heat treating
              handbook. 2011. 24.
            </li>
            <li value="15">
              Andrews, K.W., Empirical Formulae for the Calculation of Some
              Transformation Temperatures. Journal of the Iron and Steel
              Institute, 1965. 203: p. 721-727.
            </li>
            <li value="16">
              Barralis, J. and G. Maeder, Métallurgie Tome I: Métallurgie
              Physique, in Collection Scientifique ENSAM. 1982. p. 270.
            </li>
            <li value="17">
              Grange, R.A., Estimating Critical Ranges in Heat Treatment of
              Steel. Metal Progress, 1961. 79(4): p. 73-75.
            </li>
            <li value="18">
              Sugden, A. and H. Bhadeshia, Thermodynamic estimation of
              liquidus, solidus Ae 3 temperatures, and phase compositions for
              low alloy multicomponent steels. Materials science and technology,
              1989. 5(10): p. 977-984.
            </li>
            <li value="19">
              Steven, W.J.J.o.t.I. and S. Institute, The temperature of
              formation of martensite and bainite in low alloy steels, some
              effects of chemical composition. 1956. 183: p. 349-359.
            </li>
            <li value="20">
              Kung, C.Y. and J.J. Rayment, An examination of the validity of
              existing formulae for the calculation of Ms temperatures.
              Metallurgical transactions A, 1982. 13A: p. 328-331.
            </li>
            <li value="21">
              Koıstinen, D. and R.J.A.M. Marbürger, A General Equation
              Prescribing Extent of Austenite- Martensite Transformation in Pure
              Fe-C Alloy and Plain Carbon Steels. 1959. 7(1): p. 59-60.
            </li>
            <li value="22">
              Van Bohemen, S., J.J.M.S. Sietsma, and Technology, Kinetics of
              martensite formation in plain carbon steels: critical assessment
              of possible influence of austenite grain boundaries and
              autocatalysis. 2014. 30(9): p. 1024-1033.
            </li>
            <li value="23">
              Standard, A., AS 1733-1976, Method for the Determination of Grain
              Size in Metals, in Method for the Determination of Grain Size in
              Metals. 1976.
            </li>
            <li value="24">
              Ikawa, H., H. Oshige, and S. Noi, Austenite Grain Growth of Steel
              in Weld-Heat Affected Zone. Transactions of the Japan Welding
              Society, 1977. 8(2): p. 132-137.
            </li>
            <li value="25">
              Ikawa, H., et al., Austenite Grain Growth of Steels during Thermal
              Cycles. Transactions of the Japan Welding Society, 1977. 8(2): p.
              126-131.
            </li>
          </ol>
        </section>
      </div>
    )
  }
}

export default Acknowledgements
