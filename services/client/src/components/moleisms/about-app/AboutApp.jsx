/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * About Application
 *
 * @version 1.0.0
 * @author Dalton Le, Arvy Salazar, Andrew Che
 *
 * Information about the application including references and acknowledgements
 * of authors, open-source software used, and other information.
 *
 */

import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHandHoldingHeart } from '@fortawesome/pro-light-svg-icons/faHandHoldingHeart'
// import { faAtomAlt } from '@fortawesome/pro-light-svg-icons/faAtomAlt'
import { faRadiation } from '@fortawesome/pro-light-svg-icons/faRadiation'
import {
  faReact,
  faNodeJs,
  faDocker
} from '@fortawesome/free-brands-svg-icons'

import styles from './AboutApp.module.scss'


function AboutApp() {
  return (
    <div className={styles.container}>
      <h3>About Arclytics SimCCT</h3>
      <div className={styles.tagline} >
        <h5>
          Made with &nbsp;
          <FontAwesomeIcon icon={faHandHoldingHeart} size="1x" className={styles.icon}/>&nbsp;
          by NeuralDev. Powered with &nbsp;
          <FontAwesomeIcon icon={faRadiation} size="1x" className={styles.icon}/>&nbsp;
          by ANSTO.
        </h5>
      </div>
      <div className={styles.version}>
        <p><strong>Arclytics SimCCT version</strong> 1.3.0</p>
      </div>

      <section>
        <h4>Purpose</h4>
        <div className={styles.content}>
          <p>
            This software is intended as a general learning tool for estimating the solid state phase transformation
            of low alloy steels. It is primarily based on semi-empirical reaction kinetics models developed by
            Kirkaldy[1, 2] and Li[3, 4]. The package has been presented in such a way as to simplify most of the
            otherwise complex calculations necessary for predicting SSPT in low alloy steels. The trade-off is that
            these simplifications are not always the most accurate solutions available.
          </p>
          <p>
            Note that the package is not intended to provide a highly accurate solution for use in critical
            applications. For this type of work the user is recommended to consult with more comprehensive
            computational thermodynamics packages such as Thermo-Calc, Calphad, JMatPro, DICTRA etc.
          </p>
        </div>
      </section>
      <section>
        <h4>History</h4>
        <div className={styles.content}>
          <p>
            The initial work carried out with this methodology was applied to welding simulations of ferritic
            steels [5-8] using user subroutines, initially developed by Cory Hamelin (ANSTO), for the Abaqus[9]
            Finite Element Analysis (FEA) package. The advantage of a semi-empirical method is that it is
            numerically simple and therefore computationally inexpensive.
          </p>
          <p>
            When carrying out this type of simulation it is hard to visualise the Solid State Phase Transformation
            (SSPT) process when applied to a complex FEA model on an element by element basis. To aid in this
            process a standalone GUI package was developed to rapidly check and visualise the input
            parameters to be applied in the Abaqus user routines. This initial software package is stand alone
            and contains considerable additional capability related to our specific implementation of the SSPT
            Abaqus routine. The core general components of the software are being made available in the free web
            Arclytics SimCCT application.
          </p>
          <p>
            There are a number of additional aspects related to phase transformation that are dealt with in the
            Abaqus user routine that are not, at this time, included in the current online program. These include
            grain growth, hardness prediction, transformation induced plasticity (TRIP), Austenite formation,
            tempering, non-continuous cooling. Depending on the uptake of the current online software these
            may be included in the future.
          </p>
        </div>
      </section>

      <section>
        <h4>Theory</h4>
        <p>
          The online Arclytics-SimCCT package utilises the methods and ideas presented in a series of key
          publications. In this section each aspect utilised will be briefly described and the original source
          referenced. This is not considered to be an exhaustive list of the potential methods that could be
          used for this type of work.
        </p>

        <h6>Prediction of Set Point Temperatures</h6>
        <p>
          In order to estimate the SSPT of a specific low alloy steel using the method utilised here it is first
          necessary to determine a series of key parameters for the alloy. These include:
        </p>
        <ul>
          <li>
            <strong>X<sub>FE</sub></strong> - the equilibrium phase fraction of Ferrite (and hence Perlite, X<sub>PE</sub>)
          </li>
          <li>
            <strong>A<sub>e<sub>1</sub></sub></strong> - the temperature limit of Pearlite formation.
          </li>
          <li>
            <strong>A<sub>e<sub>3</sub></sub></strong> - the temperature limit of Ferrite formation.
          </li>
          <li>
            <strong>B<sub>s</sub></strong> - the temperature limit for Bainite formation.
          </li>
          <li>
            <strong>M<sub>s</sub></strong> - the temperature limit for Martensite formation.
          </li>
          <li>
            <strong>G</strong> - prior Austenite grain size (manually set in this implementation).
          </li>
        </ul>
      </section>

      <section>
        <h4>Acknowledgements</h4>

        <div className={styles.acknowledgements}>
          <p>This application was made with the help of the open-source community. Packages include:</p>
          <ul>
            <li>
              {/*<FontAwesomeIcon icon={faDocker} size="sm" className={styles.icon}/>*/}
              <a href="">Docker</a>
            </li>
            <li><a href="">Kubernetes</a></li>
            <li><a href="">conda</a></li>
            <li><a href="">Flask</a></li>
            <li><a href="">gunicorn</a></li>
            <li><a href="">Celery</a></li>
            <li>
              {/*<FontAwesomeIcon icon={faReact} size="sm" className={styles.icon}/>*/}
              <a href="">React</a>
            </li>
            <li>
              {/*<FontAwesomeIcon icon={faNodeJs} size="sm" className={styles.icon}/>*/}
              <a href="">NodeJS</a>
            </li>
            <li><a href="">MongoDB</a></li>
            <li><a href="">Redis</a></li>
            <li><a href="">Plotly</a></li>
            <li><a href="">numpy</a></li>
            <li><a href="">pandas</a></li>
            <li><a href="">jupyter</a></li>
            <li><a href="">fluentd</a></li>
            <li><a href="">Elasticsearch</a></li>
            <li><a href="">Kibana</a></li>
            <li><a href="">Elastic APM</a></li>
            <li><a href="">Marshmallow</a></li>
            <li><a href="">Flask-RESTful</a></li>
            <li><a href="">Swagger</a></li>
          </ul>
          <p>
            We would also like to acknowledge the <a>University of Wollongong (South Western Sydney campus)</a> academic
            and student services staff for their support.
          </p>
        </div>
      </section>

      <section>
        <h4>References</h4>
        <ol>
          <li value="1">
            Kirkaldy, J.C. and D. Venugopalan. Prediction of microstructure and hardenability in low alloy
            steels. in Phase Transformations in Ferrous Alloys. 1983. Philadelphia, PA.
          </li>
          <li value="2">
            Kirkaldy, J., Diffusion-controlled phase transformations in steels. Theory and applications.
            Scandinavian journal of metallurgy, 1991. 20(1): p. 50-61.
          </li>
          <li value="3">
            Li, M., Computational modeling of heat transfer and microstructure development in the
            electroslag cladding heat affected zone of low alloy steels. 1996.
          </li>
          <li value="4">
          Li, M.V., et al., A computational model for the prediction of steel hardenability. Metallurgical
          and Materials transactions B, 1998. 29(3): p. 661-672.
          </li>
          <li value="5">
            Hamelin, C.J., et al., Predicting solid-state phase transformations during welding of ferritic
            steels, in Materials Science Forum. 2012. p. 1403-1408.
          </li>
          <li value="6">
            Hamelin, C.J., et al. Predicting post-weld residual stresses in ferritic steel weldments. in
            American Society of Mechanical Engineers, Pressure Vessels and Piping Division (Publication)
            PVP. 2012.
          </li>
          <li value="7">
            Hamelin, C.J., et al. Accounting for phase transformations during welding of ferritic steels. in
            American Society of Mechanical Engineers, Pressure Vessels and Piping Division (Publication)
            PVP. 2011.
          </li>
          <li value="8">
            Hamelin, C.J., et al., Validation of a numerical model used to predict phase distribution and
            residual stress in ferritic steel weldments. Acta Materialia, 2014. 75(0): p. 1-19.
          </li>
          <li value="9">
            Abaqus. 2018, Dassault Systèmes -SIMULIA.
          </li>
          <li value="10">
            Ikawa, H., H. Oshige, and S. Noi, Austenite Grain Growth of Steel in Weld-Heat Affected Zone.
            Transactions of the Japan Welding Society, 1977. 8(2): p. 132-137.
          </li>
            Ikawa, H., et al., Austenite Grain Growth of Steels during Thermal Cycles. Transactions of the
            Japan Welding Society, 1977. 8(2): p. 126-131.
          <li value="10">
            Koıstinen, D. and R.J.A.M. Marbürger, A General Equation Prescribing Extent of Austenite-
            Martensite Transformation in Pure Fe-C Alloy and Plain Carbon Steels. 1959. 7(1): p. 59-60.
          </li>
        </ol>
      </section>
    </div>
  )
}

export default AboutApp
