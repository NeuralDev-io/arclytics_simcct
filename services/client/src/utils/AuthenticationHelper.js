/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text field component
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */

export const login = async (values, resolve, reject) => {
  fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "content-Type": "application/json"
    },
    body: JSON.stringify(values)
  })
  .then(res => {
    if (res.status === 200){
      resolve(res.json())
    }
    else if (res.status === 404){
      //return an error message as string
      res.json().then(object => reject(object.message))
    }
  })
  .catch(err => console.log(err))
}


export const signup = async (values, resolve, reject) => {
    const { email, password, firstName, lastName } = values
    fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      mode: 'cors',
      headers: {
        "content-Type": "application/json"
      },
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName
      })
    })
    .then(res => {
      if (res.status === 201){
        resolve(res.json())
      }
      else if (res.status === 400){
        //return an error message as string
        res.json().then(object => reject(object.message))
      }
    })
    .catch(err => console.log(err))
  }