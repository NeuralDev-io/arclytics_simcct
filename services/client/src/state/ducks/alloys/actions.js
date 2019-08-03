import {
  GET_ALLOYS,
  CREATE_ALLOY,
} from './types'

export const getAlloys = () => (dispatch) => {
  fetch('http://localhost:8001/global/alloys', {
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
          type: GET_ALLOYS,
          payload: data.alloys,
        })
      }
    })
    .catch(err => console.log(err))
}

export const createAlloy = alloy => (dispatch) => {
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
          type: CREATE_ALLOY,
          payload: {
            ...alloy,
            _id: data._id, // eslint-disable-line
          },
        })
      }
    })
    .catch(err => console.log(err))
}
