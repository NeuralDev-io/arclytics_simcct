/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Privacy
 *
 * @version 1.0.0
 * @author Dalton Le, Arvy Salazar, Andrew Che
 *
 * Information about the privacy policy
 *
 */

import React from 'react'

import styles from './Privacy.module.scss'


function Privacy() {
  return (
    <div className={styles.container}>
      <h3>Privacy policy</h3>

      <div className={styles.updateHistory}>
        <p>
          <strong>Last updated:</strong>
          &nbsp;October 20, 2019
        </p>
        &nbsp;
      </div>

      <section>
        <h4>Overview</h4>
        <div className={styles.content}>
          <p>
            Arclytics team is committed to providing quality services to you and
            this policy outlines our ongoing obligations to you in respect of
            how we manage your Personal Information.
          </p>
          <p>
            We have adopted the Australian Privacy Principles (APPs) contained
            in the Privacy Act 1988 (Cth) (the Privacy Act). The NPPs govern the
            way in which we collect, use, disclose, store, secure and dispose of
            your Personal Information.
          </p>
          <p>
            A copy of the Australian Privacy Principles may be obtained from the
            website of The Office of the Australian Information Commissioner at
            www.aoic.gov.au
          </p>
        </div>
      </section>

      <section>
        <h4>What is Personal Information and why do we collect it?</h4>
        <div className={styles.content}>
          <p>
            Personal Information is information or an opinion that identifies an
            individual. Examples of Personal Information we collect include:
            names , email adresses and educational experience.
          </p>
          <p>
            This Personal Information is obtained in many ways including via our
            website’s (app.arclytics.io) registration form and user profile. We
            don’t guarantee website links or policy of authorised third parties.
          </p>
          <p>
            We collect your Personal Information for the primary purpose of
            providing our services to you, providing information to our clients
            and marketing. We may also use your Personal Information for
            secondary purposes closely related to the primary purpose, in
            circumstances where you would reasonably expect such use or
            disclosure.
          </p>
          <p>
            When we collect Personal Information we will, where appropriate and
            where possible, explain to you why we are collecting the information
            and how we plan to use it.
          </p>
        </div>
      </section>

      <section>
        <h4>Sensitive Information</h4>
        <div className={styles.content}>
          <p>
            Sensitive information is defined in the Privacy Act to include
            information or opinion about such things as an individual's racial
            or ethnic origin, political opinions, membership of a political
            association, religious or philosophical beliefs, membership of a
            trade union or other professional body, criminal record or health
            information.
          </p>
          <p>Sensitive information will be used by us only:</p>
          <ul>
            <li>
              To use for user analytics for discovering the demographic of the
              application.
            </li>
            <li>With your consent; or where required or authorised by law.</li>
          </ul>
        </div>
      </section>

      <section>
        <h4>Third Parties</h4>
        <div className={styles.content}>
          <p>
            Where reasonable and practicable to do so, we will collect your
            Personal Information only from you. However, in some circumstances
            we may be provided with information by third parties. In such a case
            we will take reasonable steps to ensure that you are made aware of
            the information provided to us by the third party.
          </p>
        </div>
      </section>

      <section>
        <h4>Disclosure of Personal Information</h4>
        <div className={styles.content}>
          <p>
            Your Personal Information may be disclosed in a number of
            circumstances including the following:
          </p>
          <ul>
            <li>
              Third parties where you consent to the use or disclosure; and
            </li>
            <li>Where required or authorised by law.</li>
          </ul>
        </div>
      </section>

      <section>
        <h4>Security of Personal Information</h4>
        <div className={styles.content}>
          <p>
            Your Personal Information is stored in a manner that reasonably
            protects it from misuse and loss and from unauthorized access,
            modification or disclosure.
          </p>
          <p>
            When your Personal Information is no longer needed for the purpose
            for which it was obtained, we will take reasonable steps to destroy
            or permanently de-identify your Personal Information. However, most
            of the Personal Information is or will be stored in client files
            which will be kept by us for a minimum of 7 years.
          </p>
        </div>
      </section>

      <section>
        <h4>Access to your Personal Information</h4>
        <div className={styles.content}>
          <p>
            You may access the Personal Information we hold about you and to
            update and/or correct it, subject to certain exceptions. If you wish
            to access your Personal Information, please contact us in writing.
          </p>
          <p>
            The NeuralDev team will not charge any fee for your access request,
            but may charge an administrative fee for providing a copy of your
            Personal Information. Additionally, your Personal Information can
            also viewed in the user profile page of the web application.
          </p>
          <p>
            In order to protect your Personal Information we may require
            identification from you before releasing the requested information.
          </p>
        </div>
      </section>

      <section>
        <h4>Maintaining the Quality of your Personal Information</h4>
        <div className={styles.content}>
          <p>
            It is important to us that your Personal Information is up to date.
            We will take reasonable steps to make sure that your Personal
            Information is accurate, complete and up-to-date. If you find that
            the information we have is not up to date or is inaccurate, please
            advise us as soon as practicable so we can update our records and
            ensure we can continue to provide quality services to you.
          </p>
        </div>
      </section>

      <section>
        <h4>Policy Updates</h4>
        <div className={styles.content}>
          <p>
            This Policy may change from time to time and is available on our
            website at&nbsp;
            <a href="https://app.arclytics.io/about/privacy">
              app.arclytics.io/about/privacy
            </a>
            .
          </p>
        </div>
      </section>

      <section>
        <h4>Privacy Policy Complaints and Enquiries</h4>
        <div className={styles.content}>
          <p>
            If you have any queries or complaints about our Privacy Policy
            please contact us at:
          </p>
          <p>NeuralDev</p>
          <p>
            <a href="mailto: admin@neuraldev.io">admin@neuraldev.io</a>
          </p>
        </div>
      </section>
    </div>
  )
}

export default Privacy
