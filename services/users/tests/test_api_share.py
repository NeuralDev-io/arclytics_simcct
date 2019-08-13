# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""test_api_users.py: 

This script will run all tests on the Users endpoints.
"""

import json
import unittest
from datetime import datetime

from bson import ObjectId
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import (
    User, UserProfile, AdminProfile, Element, Alloy, Configuration,
    SharedSimulation, AlloyType, AlloyStore
)
from users_app.token import (
    generate_confirmation_token, generate_url,
    generate_promotion_confirmation_token,
    generate_shared_simulation_signature, generate_url_with_signature,
    confirm_signature
)

logger = AppLogger(__name__)

# TODO(davidmatthews1004@gmail.com) If possible, import this so its not
#  repeated.
def log_test_user_in(self, user: User, password: str) -> str:
    """Log in a test user and return their token"""
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': user.email,
                'password': password
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['token']
        return token

class TestShareService(BaseTestCase):
    """Test for sharing simulations via link and email"""

    def test_share_configuration_link_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified=True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')

    def test_share_configuration_link_no_data(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_share_configuration_link_key_error(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name'
                                },
                                'weld': {
                                    'name':
                                    'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        }, {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Key error.')

    def test_share_configuration_single_email_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 'davidmatthews1004@gmail.com',
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email(s) sent.')

    def test_share_configuration_multiple_emails_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': [
                            'davidmatthews1004@gmail.com',
                            'brickmatic479@gmail.com'
                        ],
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email(s) sent.')

    def test_share_configuration_email_no_data(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_share_configuration_email_no_email(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name':
                                    'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        }, {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name':
                                    'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        }, {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name':
                                    'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        }, {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No email addresses provided.')

    def test_share_configuration_email_invalid_email_type(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 1234,
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name':
                                    'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        }, {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name':
                                    'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        }, {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name':
                                    'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        }, {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email address type.')

    def test_share_configuration_email_invalid_email(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 'invalidemail@com',
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name':
                                    'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        }, {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name':
                                    'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        }, {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name':
                                    'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        }, {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

if __name__ == '__main__':
    unittest.main()