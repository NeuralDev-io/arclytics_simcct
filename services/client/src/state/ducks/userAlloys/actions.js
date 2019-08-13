import {
  CREATE_USER_ALLOY,
  RETRIEVE_USER_ALLOYS,
  RETRIEVE_USER_ALLOY_DETAIL,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
} from './types'

// TODO(andrew@neuraldev.io): Comment on each function about the expected input
//  and some more information about the expected response.

export const postUserAlloy = () => (alloy, dispatch) => {
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
          payload: data.data, // Response returns {"status": "success", "data": {}}
        })
      } else { throw new Error(data.message) }
      // TODO(andrew@neuraldev.io): Should consider giving the user another change
      //  to post or change the alloy rather than throwing an error.
    })
}

export const getUserAlloys = () => (dispatch) => {
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
        console.log(data)
        dispatch({
          type: RETRIEVE_USER_ALLOYS,
          payload: data.data, // Response returns {"status": "success", "data": [...]}
        })
      }
    })
    .catch(err => console.log(err))
}

export const getUserAlloyDetail = () => (alloyId, dispatch) => {
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

export const putUserAlloy = () => (alloy, alloyId, dispatch) => {
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

export const deleteUserAlloys = () => (alloyId, dispatch) => {
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
