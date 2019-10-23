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
              Ikawa, H., H. Oshige, and S. Noi, Austenite Grain Growth of Steel
              in Weld-Heat Affected Zone. Transactions of the Japan Welding
              Society, 1977. 8(2): p. 132-137.
            </li>
            <li value="11">
              Ikawa, H., et al., Austenite Grain Growth of Steels during Thermal
              Cycles. Transactions of the Japan Welding Society, 1977. 8(2): p.
              126-131.
            </li>
            <li value="12">
              Koıstinen, D. and R.J.A.M. Marbürger, A General Equation
              Prescribing Extent of Austenite- Martensite Transformation in Pure
              Fe-C Alloy and Plain Carbon Steels. 1959. 7(1): p. 59-60.
            </li>
          </ol>
        </section>
      </div>
    )
  }
}

export default Acknowledgements
