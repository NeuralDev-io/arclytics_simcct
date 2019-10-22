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
import { faRadiation } from '@fortawesome/pro-light-svg-icons/faRadiation'

import styles from './AboutApp.module.scss'

const AboutApp = () => (
  <div className={styles.container}>
    <h3>About Arclytics SimCCT</h3>
    <div className={styles.tagline}>
      <h5>
        Made with &nbsp;
        <FontAwesomeIcon
          icon={faHandHoldingHeart}
          size="1x"
          className={styles.icon}
        />
        &nbsp; by NeuralDev. Powered with &nbsp;
        <FontAwesomeIcon
          icon={faRadiation}
          size="1x"
          className={styles.icon}
        />
        &nbsp; by ANSTO.
      </h5>
    </div>
    <div className={styles.version}>
      <p>
        <strong>Arclytics SimCCT version</strong>
        &nbsp; 1.3.0
      </p>
    </div>

    <section>
      <h4>Purpose</h4>
      <div className={styles.content}>
        <p>
          This software is intended as a general learning tool for
          estimating the solid state phase transformation of low alloy
          steels. It is primarily based on semi-empirical reaction kinetics
          models developed by Kirkaldy[1, 2] and Li[3, 4]. The package has
          been presented in such a way as to simplify most of the otherwise
          complex calculations necessary for predicting SSPT in low alloy
          steels. The trade-off is that these simplifications are not always
          the most accurate solutions available.
        </p>
        <p>
          Note that the package is not intended to provide a highly accurate
          solution for use in critical applications. For this type of work
          the user is recommended to consult with more comprehensive
          computational thermodynamics packages such as Thermo-Calc,
          Calphad, JMatPro, DICTRA etc.
        </p>
      </div>
    </section>
    <section>
      <h4>History</h4>
      <div className={styles.content}>
        <p>
          The initial work carried out with this methodology was applied to
          welding simulations of ferritic steels [5-8] using user
          subroutines, initially developed by Cory Hamelin (ANSTO), for the
          Abaqus[9] Finite Element Analysis (FEA) package. The advantage of
          a semi-empirical method is that it is numerically simple and
          therefore computationally inexpensive.
        </p>
        <p>
          When carrying out this type of simulation it is hard to visualise
          the Solid State Phase Transformation (SSPT) process when applied
          to a complex FEA model on an element by element basis. To aid in
          this process a standalone GUI package was developed to rapidly
          check and visualise the input parameters to be applied in the
          Abaqus user routines. This initial software package is stand alone
          and contains considerable additional capability related to our
          specific implementation of the SSPT Abaqus routine. The core
          general components of the software are being made available in the
          free web Arclytics SimCCT application.
        </p>
        <p>
          There are a number of additional aspects related to phase
          transformation that are dealt with in the Abaqus user routine that
          are not, at this time, included in the current online program.
          These include grain growth, hardness prediction, transformation
          induced plasticity (TRIP), Austenite formation, tempering,
          non-continuous cooling. Depending on the uptake of the current
          online software these may be included in the future.
        </p>
      </div>
    </section>

    <section>
      <h4>Theory</h4>
      <p>
        The online Arclytics-SimCCT package utilises the methods and ideas
        presented in a series of key publications. In this section each
        aspect utilised will be briefly described and the original source
        referenced. This is not considered to be an exhaustive list of the
        potential methods that could be used for this type of work.
      </p>

      <h6>Prediction of Set Point Temperatures</h6>
      <p>
        In order to estimate the SSPT of a specific low alloy steel using
        the method utilised here it is first necessary to determine a series
        of key parameters for the alloy. These include:
      </p>
      <ul>
        <li>
          <strong>
            X<sub>FE</sub>
          </strong>
          &nbsp;- the equilibrium phase fraction of Ferrite (and hence
          Perlite, X<sub>PE</sub>)
        </li>
        <li>
          <strong>
            A<sub>e1</sub>
          </strong>
          &nbsp;- the temperature limit of Pearlite formation.
        </li>
        <li>
          <strong>
            A<sub>e3</sub>
          </strong>
          &nbsp;- the temperature limit of Ferrite formation.
        </li>
        <li>
          <strong>
            B<sub>s</sub>
          </strong>
          &nbsp;- the temperature limit for Bainite formation.
        </li>
        <li>
          <strong>
            M<sub>s</sub>
          </strong>
          &nbsp;- the temperature limit for Martensite formation.
        </li>
        <li>
          <strong>G</strong>
          &nbsp;- prior Austenite grain size (manually set in this
          implementation).
        </li>
      </ul>
    </section>
  </div>
)

export default AboutApp
