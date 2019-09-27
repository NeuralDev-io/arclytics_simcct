import { init as initAPM } from '@elastic/apm-rum'
import { APM_URL } from './constants'

// The APM Real User Monitoring service
const apm = initAPM({
  // Set required service name (allowed characters: a-z, A-Z, 0-9, -, _, and space)
  serviceName: 'client',
  // Set custom APM Server URL (default: http://localhost:8200)
  // serverUrl: `${process.env.REACT_APP_APM_URL}`,
  serverUrl: APM_URL,
  // Set service version (required for sourcemap feature)
  // serviceVersion: '0.9',

  // Environment where the service being monitored is deployed, e.g. "production" or "development"
  environment: process.env.NODE_ENV,

  // This option sets the name for the page load transaction.
  // Note:
  // This is not working with `window.location.pathname` as we are using
  // React-Router which uses a Shadow DOM and doesn't have windows.
  // Pass the pageName into the APM agent as a configuration option
  // pageLoadTransactionName: pageName,
  pageLoadTransactionName: 'client',
})

export default apm
