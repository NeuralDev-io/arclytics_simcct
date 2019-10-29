/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Actions used to make API requests to the `users` and `simcct` microservice to
 * handle operations on Global and User Saved Alloys including creating, retrieving,
 * updating, and deleting an alloy. The response will be dispatched to a reducer a
 * nd sent to the `UserAlloys`
 * component.
 *
 *
 * @version 1.1.1
 * @author Dalton Le and Andrew Che
 */


import {
  GET_GLOBAL_ALLOYS,
  CREATE_GLOBAL_ALLOY,
  UPDATE_GLOBAL_ALLOY,
  DELETE_GLOBAL_ALLOY,
  GET_USER_ALLOYS,
  CREATE_USER_ALLOY,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
} from './types'
import { addFlashToast } from '../toast/actions'
import { SIMCCT_URL } from '../../../constants'
import { logError } from '../../../api/LoggingHelper'
import { forceSignIn } from '../redirector/actions'

// Change the ports for which server

const getAlloys = type => (dispatch) => {
  /**
   * API call to `simcct` or `users` server to get all alloys stored in theGlobal
   * database or the User's Document respectively. The Users are identified by
   * the JWT token passed as the Authorization in the header.
   * @param {type} the type of alloys endpoint to use.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   *   "data": [{"_id": ..., "name": ..., "compositions": [...]}, {...}]
   * }
   */

  dispatch({
    type: type === 'global' ? GET_GLOBAL_ALLOYS : GET_USER_ALLOYS,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/${type}/alloys`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status === 404) { return { status: 'success', data: [] } }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Counld\'t retrieve alloy list',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
        dispatch({
          type: type === 'global' ? GET_GLOBAL_ALLOYS : GET_USER_ALLOYS,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? GET_GLOBAL_ALLOYS : GET_USER_ALLOYS,
          payload: res.data || [],
          status: 'success',
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'alloys.actions.getAlloys', err.stack)
    })
}

const createAlloy = (type, alloy) => dispatch => (
  /**
   * API call to `users` or `simcct` server to create a new alloy which is stored
   * in the Global database or User's Document. The Users are identified by the
   * JWT token passed as the Authorization in the header.
   * @param {type} the type of alloys endpoint to use.
   * @param {alloy} a valid Alloy object.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   *   "data": {"_id": ..., "name": ..., "compositions": [...]}
   * }
   */
  fetch(`${SIMCCT_URL}/${type}/alloys`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(alloy),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 201) {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? CREATE_GLOBAL_ALLOY : CREATE_USER_ALLOY,
          payload: {
            ...alloy,
            _id: res.data._id, // eslint-disable-line
          },
        })
        addFlashToast({
          message: `Alloy ${alloy.name} created`,
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'alloys.actions.createAlloy', err.stack)
    })
)

const updateAlloy = (type, alloy) => (dispatch) => {
  fetch(`${SIMCCT_URL}/${type}/alloys/${alloy._id}`, { // eslint-disable-line
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: alloy.name,
      compositions: alloy.compositions,
    }),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? UPDATE_GLOBAL_ALLOY : UPDATE_USER_ALLOY,
          payload: res.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'alloys.actions.updateAlloy', err.stack)
    })
}

const deleteAlloy = (type, alloyId) => (dispatch) => {
  /**
   * API call to `simcct` or `users` server to delete an alloy which is stored in
   * the Global database or User's Document respectively. The alloy is identified
   * by the `alloyId` parameter in the request url. The Users are identified by
   * the JWT token passed as the Authorization in the header.
   * @param {type} the type of alloys endpoint to use.
   * @param {alloyId} a valid Alloy ObjectId.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   * }
   */
  fetch(`${SIMCCT_URL}/${type}/alloys/${alloyId}`, {
    method: 'DELETE',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 202) {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? DELETE_GLOBAL_ALLOY : DELETE_USER_ALLOY,
          payload: alloyId,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'alloys.actions.deleteAlloy', err.stack)
    })
}

export const getGlobalAlloys = () => getAlloys('global')
export const createGlobalAlloy = alloy => createAlloy('global', alloy)
export const updateGlobalAlloy = alloy => updateAlloy('global', alloy)
export const deleteGlobalAlloy = alloyId => deleteAlloy('global', alloyId)

export const getUserAlloys = () => getAlloys('user')
export const createUserAlloy = alloy => createAlloy('user', alloy)
export const updateUserAlloy = alloy => updateAlloy('user', alloy)
export const deleteUserAlloy = alloyId => deleteAlloy('user', alloyId)
