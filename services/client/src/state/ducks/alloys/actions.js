import {
  GET_GLOBAL_ALLOYS,
  CREATE_GLOBAL_ALLOY,
  UPDATE_GLOBAL_ALLOY,
  DELETE_GLOBAL_ALLOY,
} from './types'

export const getGlobalAlloys = () => (dispatch) => {
  fetch('http://localhost:8001/global/alloys', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: GET_GLOBAL_ALLOYS,
          payload: data.alloys,
        })
      }
    })
    .catch(err => console.log(err))
}

export const createGlobalAlloy = alloy => (dispatch) => {
  fetch('http://localhost:8001/global/alloys', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CREATE_GLOBAL_ALLOY,
          payload: {
            ...alloy,
            _id: data._id, // eslint-disable-line
          },
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateGlobalAlloy = alloy => (dispatch) => {
  fetch('http://localhost:8001/global/alloys', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(alloy),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_GLOBAL_ALLOY,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const deleteGlobalAlloy = alloyId => (dispatch) => {
  fetch(`http://localhost:8001/global/alloys/${alloyId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: DELETE_GLOBAL_ALLOY,
          payload: alloyId,
        })
      }
    })
    .catch(err => console.log(err))
}
