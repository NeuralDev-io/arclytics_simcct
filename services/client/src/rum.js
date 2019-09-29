/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides a Real User Monitoring Elastic APM service by configuring how it
 * connects to the APM server. The configurations are for the JavaScript
 * client found in the documentation listed below.
 *
 * [1] https://www.elastic.co/guide/en/apm/agent/rum-js/4.x/index.html
 *
 * @version 0.2.0
 * @author Andrew Che
 */

// import { init as initAPM } from '@elastic/apm-rum'
// import { APM_URL, CLIENT_ENV } from './constants'

/*
*
* DECISION:
* Not using this as in production, we cannot find a way to expose the APM
* server from the cluster. We were able to add a SSL/TLS certificate to the
* server but were unable to this client frontend connect with it through an
* ingress controller. This may be revisited at a later stage.
*
* We continue to add this here because during development it works just fine
* inside a Docker cluster of containers.
*
* */

// eslint-disable-next-line import/no-mutable-exports
// let apm = null
//
// if (CLIENT_ENV === 'development') {
//   // The APM Real User Monitoring service
//   apm = initAPM({
//     // Set required service name (allowed characters: a-z, A-Z, 0-9, -, _, and space)
//     serviceName: 'client',
//     // Set custom APM Server URL (default: http://localhost:8200)
//     // serverUrl: `${process.env.REACT_APP_APM_URL}`,
//     serverUrl: APM_URL,
//     // Set service version (required for sourcemap feature)
//     // serviceVersion: '0.9',
//
//     // Environment where the service being monitored is deployed,
//     // e.g. "production" or "development"
//     environment: CLIENT_ENV,
//
//     // This option sets the name for the page load transaction.
//     // Note:
//     // This is not working with `window.location.pathname` as we are using
//     // React-Router which uses a Shadow DOM and doesn't have windows.
//     // Pass the pageName into the APM agent as a configuration option
//     // pageLoadTransactionName: pageName,
//     pageLoadTransactionName: 'client',
//   })
// }
//
// export default apm
