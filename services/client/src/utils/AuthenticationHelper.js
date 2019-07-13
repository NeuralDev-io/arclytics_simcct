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
        res.json().then(object => reject(object.message))
      }
    })
    .catch(err => console.log(err))
  }