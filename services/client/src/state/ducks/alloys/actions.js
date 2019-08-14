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

// Change the ports for which server
const getPort = type => (type === 'global' ? 8001 : 8000)

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
  fetch(`http://localhost:${getPort(type)}/${type}/alloys`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? GET_GLOBAL_ALLOYS : GET_USER_ALLOYS,
          payload: res.data || [],
        })
      }
    })
    .catch(err => console.log(err))
}

const createAlloy = (type, alloy) => (dispatch) => {
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
  fetch(`http://localhost:${getPort(type)}/${type}/alloys`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? CREATE_GLOBAL_ALLOY : CREATE_USER_ALLOY,
          payload: {
            ...alloy,
            _id: res.data._id, // eslint-disable-line
          },
        })
      }
    })
    .catch(err => console.log(err))
}

const updateAlloy = (type, alloy) => (dispatch) => {
  fetch(`http://localhost:${getPort(type)}/${type}/alloys`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? UPDATE_GLOBAL_ALLOY : UPDATE_USER_ALLOY,
          payload: res.data,
        })
      }
    })
    .catch(err => console.log(err))
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
  fetch(`http://localhost:${getPort(type)}/${type}/alloys/${alloyId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: type === 'global' ? DELETE_GLOBAL_ALLOY : DELETE_USER_ALLOY,
          payload: alloyId,
        })
      }
    })
    .catch(err => console.log(err))
}

export const getGlobalAlloys = () => getAlloys('global')
export const createGlobalAlloys = alloy => createAlloy('global', alloy)
export const updateGlobalAlloys = alloy => updateAlloy('global', alloy)
export const deleteGlobalAlloys = alloyId => deleteAlloy('global', alloyId)

export const getUserAlloys = () => getAlloys('user')
export const createUserAlloy = alloy => createAlloy('user', alloy)
export const updateUserAlloy = alloy => updateAlloy('user', alloy)
export const deleteUserAlloy = alloyId => deleteAlloy('user', alloyId)
