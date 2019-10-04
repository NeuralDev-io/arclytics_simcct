/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to grab Analytics data for
 * the purpose of charting.
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */

import { ARC_URL } from '../constants'

// TODO(andrew@neuraldev.io): Ensure this is non-blocking.
// eslint-disable-next-line import/prefer-default-export
export const log = async () => fetch(
  `${ARC_URL}/users/profile`, {
    method: 'GET',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  },
)
