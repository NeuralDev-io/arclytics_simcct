/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Actions used to make API requests to the `users` microservice to handle operations
 * on User Saved Alloys including creating, retrieving, updating, and deleting an
 * alloy. The response will be dispatched to a reducer and sent to the `UserAlloys`
 * component.
 *
 *
 * @version 0.1.0
 * @author Andrew Che
 */

import {
  CREATE_USER_ALLOY,
  RETRIEVE_USER_ALLOYS,
  RETRIEVE_USER_ALLOY_DETAIL,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
} from './types'

// TODO(andrew@neuraldev.io): Comment on each function about the expected input
//  and some more information about the expected response.

export const postUserAlloy = alloy => (dispatch) => {
  /**
   * API call to `users` server to create a new alloy which is stored in the User's
   * Document. The Users are identified by the JWT token passed as the Authorization
   * in the header.
   * @param {alloy} a valid Alloy object.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   *   "data": {"_id": ..., "name": ..., "compositions": [...]}
   * }
   */
  fetch('http://localhost:8000/user/alloys', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'success') {
        // Dispatch the response to the reducer
        dispatch({
          type: CREATE_USER_ALLOY,
          payload: data.data,
        })
      } else { throw new Error(data.message) }
      // TODO(andrew@neuraldev.io): Should consider giving the user another chance
      //  to post or change the alloy rather than throwing an error.
    })
    .catch(err => console.log(err))
}

export const getUserAlloys = () => (dispatch) => {
  /**
   * API call to `users` server to get all alloys  stored in the User's Document.
   * The Users are identified by the JWT token passed as the Authorization in the header.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   *   "data": [{"_id": ..., "name": ..., "compositions": [...]}, {...}]
   * }
   */
  fetch('http://localhost:8000/user/alloys', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      // More chance of failing than succeeding TBH
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        // Dispatch the response to the reducer
        dispatch({
          type: RETRIEVE_USER_ALLOYS,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const getUserAlloyDetail = alloyId => (dispatch) => {
  fetch(`http://localhost:8000/user/alloys/${alloyId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'success') {
        // Dispatch the response to the reducer
        dispatch({
          type: RETRIEVE_USER_ALLOY_DETAIL,
          payload: data.data, // Response returns {"status": "success", "data": {}}
        })
      } else { throw new Error(data.message) }
    })
    .catch(err => console.log(err))
}

export const putUserAlloy = (alloy, alloyId) => (dispatch) => {
  fetch(`http://localhost:8000/user/alloys/${alloyId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'success') {
        // Response returns {"status": "success"}
        // Dispatch the response to the reducer
        dispatch({
          type: UPDATE_USER_ALLOY,
        })
      } else { throw new Error(data.message) }
    })
    .catch(err => console.log(err))
}

export const deleteUserAlloy = alloyId => (dispatch) => {
  /**
   * API call to `users` server to delete an alloy which is stored in the User's
   * Document. The alloy is identified by the `alloyId` parameter in the request
   * url. The Users are identified by the JWT token passed as the Authorization
   * in the header.
   * @param {alloyId} a valid Alloy ObjectId.
   * @param {dispatch} the Redux `dispatch()` function which will define the `type` of
   * reducer to use as defined in `src/state/ducks/userAlloys/reducers.js`.
   * If successful, the response will be:
   * {
   *   "status": "success",
   * }
   */
  fetch(`http://localhost:8000/user/alloys/${alloyId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'success') {
        // Response returns {"status": "success"}
        // Dispatch the response to the reducer
        dispatch({
          type: DELETE_USER_ALLOY,
        })
      } else { throw new Error(data.message) }
    })
    .catch(err => console.log(err))
}
