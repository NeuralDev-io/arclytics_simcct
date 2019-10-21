/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * About Application
 *
 * @version 1.0.0
 * @author Dalton Le, Arvy Salazar, Andrew Che
 *
 * The disclaimer information for the application.
 *
 */

import React from 'react'

import styles from './Disclaimer.module.scss'


function Disclaimer() {
  return (
    <div className={styles.container}>
      <h3>Disclaimer</h3>

      <div className={styles.updateHistory}>
        <p><strong>Last updated:</strong> October 20, 2019</p>&nbsp;
      </div>

      <section>
        <h4>Overview</h4>
        <div className={styles.content}>
          <p>
            This program including information contained within it is provided for evaluation/demonstration purposes
            only. It should not be used for production purposes. The analyst assumes all responsibility for the use,
            misuse or inability to use this information and in no event shall the Australian Nuclear Science and
            Technology Organisation or the NeuralDev team have any liability for damages whatsoever, arising from or in
            connection thereof.
          </p>
          <p>
            This information is provided “as is” and without warranties as to the performance, merchantability, fitness
            for a particular purpose, or any other warranties whether expressed or implied.
          </p>
          <p>
            THIS PROGRAM SHOULD NOT BE RELIED ON FOR SOLVING A PROBLEM WHOSE INCORRECT SOLUTION COULD RESULT IN INJURY
            TO A PERSON OR LOSS OF PROPERTY
          </p>
        </div>
      </section>

      <section>
        <h4>External Links Disclaimer</h4>
        <div className={styles.content}>
          <p>
            Arclytics SimCCT may contain links to external websites that are not provided or maintained by or in any
            affiliated with the NeuralDev team or ANSTO. Please note that the Arclytics does not guarantee the accuracy,
            relevance, timeliness or completeness of any information on these external websites.
          </p>
        </div>
      </section>

    </div>
  )
}

export default Disclaimer
