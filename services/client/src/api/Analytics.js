/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to grab Analytics data for
 * the purpose of charting.
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */

import { ARC_URL } from '../constants'
import { logError } from './LoggingHelper'


export const getNerdyStatsData = async () => {
  /**
   * Get the summary stats for the Users Analytics page. This function will
   * always return a resolved promise with the state being the data in the
   * response if any.
   *
   */
  let call
  try {

    call = await fetch(`${ARC_URL}/users/stats`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status === 401) throw new Error('Unauthenticated')
        if (res.status === 403) throw new Error('Unauthorised')
        return res.json()
      })
      .then(res => res)

  } catch (e) {

    logError(
      e.toString(),
      e.message,
      'Analytics.getNerdyStatsData',
      e.stack
    )
    return {
      status: 'fail',
      data: undefined
    }

  }
  return call
}


export const getProfileAnalyticsData = async () => {
  /**
   * Get the profile data to plot bar charts for the Users Analytics page.
   * This function will always return a resolved promise with the state being
   * the data in the response if any.
   *
   */
  let call
  try {
    call = await fetch(`${ARC_URL}/users/profile`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403)  {
          throw new Error('Unauthorised')
        }
        return res.json()
      })
      .then(res => res)

  } catch (e) {
    logError(
      e.toString(),
      e.message,
      'Analytics.getProfileAnalyticsData',
      e.stack
    )
    return {
      status: 'fail',
      data: undefined
    }
  }
  return call
}


export const getLoginLocationData = async () => {
  /**
   * Get the data for location data to plot the Mapbox Density chart
   * on the User Analytics page. This function will always return a
   * resolved promise with the state being the data in the response if any.
   *
   */
  let call
  try {
    call = await fetch(`${ARC_URL}/users/login/map`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403)  {
          throw new Error('Unauthorised')
        }
        return res.json()
      })
      .then(res => res)

  } catch (e) {
    logError(
      e.toString(),
      e.message,
      'Analytics.getLoginLocationData',
      e.stack
    )
    return {
      status: 'fail',
      data: undefined
    }
  }
  return call
}

export const getGeneralStatsData = async () => {
  /**
   * Get the summary stats for the App Analytics page. This function will
   * always return a resolved promise with the state being the data in the
   * response if any.
   *
   */
  let call
  try {
    call = await fetch(`${ARC_URL}/app/stats`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status === 401) throw new Error('Unauthenticated')
        if (res.status === 403) throw new Error('Unauthorised')
        return res.json()
      })
      .then(res => res)

  } catch (e) {

    logError(
      e.toString(),
      e.message,
      'Analytics.getGeneralStatsData',
      e.stack
    )
    return {
      status: 'fail',
      data: undefined
    }

  }
  return call
}


export const getLiveLoginData = async () => {
  /**
   * Get the data for the live login location stats to plot the time series chart
   * on the Application Analytics page. This function will always return a
   * resolved promise with the state being the data in the response if any.
   *
   */
  let call
  try {
    call = await fetch(`${ARC_URL}/app/logged_in_data`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403)  {
          throw new Error('Unauthorised')
        }
        return res.json()
      })
      .then(res => res)

  } catch (e) {

    logError(
      e.toString(),
      e.message,
      'Analytics.getLiveLoginData',
      e.stack
    )
    return {
      status: 'fail',
      data: undefined
    }

  }
  return call
}
