import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
} from './types'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  fetch('http://localhost:8000/user', {
    method: 'GET',
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
          type: GET_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const createUserProfile = values => (dispatch) => {
  console.log(values.profile.aim, values.profile.highest_education, values.profile.sci_tech_exp, values.profile.phase_transform_exp)
  fetch('http://localhost:8000/user', {
    method: 'PATCH',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CREATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateUserProfile = values => (dispatch) => {
  fetch('http://localhost:8000/user_profile', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}
