import {
  GET_USER_PROFILE,
} from './types'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  const fake = {
    _id: 'string',
    email: 'iron_man@avengers.io',
    first_name: 'Tony',
    last_name: 'Stark',
    active: true,
    admin: true,
    created: '2019-08-05T21:37:14.896Z',
    verified: false,
    last_updated: '2019-08-05T21:37:14.896Z',
    last_login: '2019-08-05T21:37:14.896Z',
    profile: {
      aim: 'string',
      highest_education: 'string',
      sci_tech_exp: 'string',
      phase_transform_exp: 'string',
    },
    admin_profile: {
      mobile_number: '0433333333',
      position: 'dunno',
      verified: true,
    },
  }
  dispatch({
    type: GET_USER_PROFILE,
    payload: fake,
  })

  fetch('http://localhost:8000/user/profile', {
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
          payload: data,
        })
      }
    })
    .catch(err => console.log(err))
}
