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

const getAlloys = type => (dispatch) => {
  fetch(`http://localhost:8001/${type}/alloys`, {
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
          type: type === 'global' ? GET_GLOBAL_ALLOYS : GET_USER_ALLOYS,
          payload: data.alloys,
        })
      }
    })
    .catch(err => console.log(err))
}

const createAlloy = (type, alloy) => (dispatch) => {
  fetch(`http://localhost:8001/${type}/alloys`, {
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
          type: type === 'global' ? CREATE_GLOBAL_ALLOY : CREATE_USER_ALLOY,
          payload: {
            ...alloy,
            _id: data._id, // eslint-disable-line
          },
        })
      }
    })
    .catch(err => console.log(err))
}

const updateAlloy = (type, alloy) => (dispatch) => {
  fetch(`http://localhost:8001/${type}/alloys`, {
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
          type: type === 'global' ? UPDATE_GLOBAL_ALLOY : UPDATE_USER_ALLOY,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

const deleteAlloy = (type, alloyId) => (dispatch) => {
  fetch(`http://localhost:8001/${type}/alloys/${alloyId}`, {
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
export const updateUserAlloy = alloy => updateUserAlloy('user', alloy)
export const deleteUserAlloy = alloyId => deleteUserAlloy('user', alloyId)

export const getAllAlloys = () => {
  getAlloys('global')
  getAlloys('user')
}
