# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_ratings.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'David Matthews'
__email__ = 'davidmatthews1004@gmail.com'
__status__ = 'development'
__date__ = '2019.08.27'
"""test_api_ratings.py: 

This script will run all tests on the Ratings and feedback endpoints.
"""

import os
import json
import unittest

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import User, Feedback, AdminProfile
from tests.test_api_users import log_test_user_in

logger = AppLogger(__name__)


class TestRatingsService(BaseTestCase):
    """Tests for Ratings and feedback endpoints"""

    def test_post_rating_no_data(self):
        mace = User(
            email='mace@arclytics.io', first_name='Mace', last_name='Windu'
        )
        mace.set_password('ThisPartysOver')
        mace.save()
        token = log_test_user_in(self, mace, 'ThisPartysOver')

        with self.client:
            resp = self.client.post(
                '/user/rating',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_post_rating_no_rating(self):
        plo = User(
            email='plokoon@arclytics.io', first_name='Plo', last_name='Koon'
        )
        plo.set_password('WhenYouAskForTrouble')
        plo.save()
        token = log_test_user_in(self, plo, 'WhenYouAskForTrouble')

        with self.client:
            resp = self.client.post(
                '/user/rating',
                data=json.dumps({'invalid_key': 'some_value'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No rating provided.')

    def test_post_rating_invalid_rating(self):
        ahsoka = User(
            email='ahsoka@arclytics.io', first_name='Ahsoka', last_name='Tano'
        )
        ahsoka.set_password('WhenYouAskForTrouble')
        ahsoka.save()
        token = log_test_user_in(self, ahsoka, 'WhenYouAskForTrouble')

        with self.client:
            resp = self.client.post(
                '/user/rating',
                data=json.dumps({'rating': '10'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Rating validation error.')

    def test_post_rating_success(self):
        rex = User(
            email='rex@arclytics.io', first_name='Captain', last_name='Rex'
        )
        rex.set_password('ExperienceOutranksEverything')
        rex.save()
        token = log_test_user_in(self, rex, 'ExperienceOutranksEverything')

        with self.client:
            resp = self.client.post(
                '/user/rating',
                data=json.dumps({'rating': '5'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], f'Rating submitted by {rex.email}.'
            )

            rex_updated = User.objects.get(email=rex.email)
            self.assertEqual(rex_updated['ratings'][0]['rating'], 5)

    def test_post_multiple_ratings_success(self):
        cody = User(
            email='cody@arclytics.io',
            first_name='Commander',
            last_name='Cody'
        )
        cody.set_password('BlastHim')
        cody.save()
        token = log_test_user_in(self, cody, 'BlastHim')

        with self.client:
            resp_1 = self.client.post(
                '/user/rating',
                data=json.dumps({'rating': '3'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            resp_2 = self.client.post(
                '/user/rating',
                data=json.dumps({'rating': '5'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')
            self.assertEqual(
                data_1['message'], f'Rating submitted by {cody.email}.'
            )
            data_2 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')
            self.assertEqual(
                data_2['message'], f'Rating submitted by {cody.email}.'
            )

            cody_updated = User.objects.get(email=cody.email)
            self.assertEqual(cody_updated['ratings'][0]['rating'], 3)
            self.assertEqual(cody_updated['ratings'][1]['rating'], 5)

    def test_post_feedback_no_data(self):
        echo = User(
            email='echo@arclytics.io',
            first_name='Arc Trooper',
            last_name='Echo'
        )
        echo.set_password('WeGotToFollowOrders')
        echo.save()
        token = log_test_user_in(self, echo, 'WeGotToFollowOrders')

        with self.client:
            resp = self.client.post(
                '/user/feedback',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_post_feedback_missing_fields(self):
        fives = User(
            email='fives@arclytics.io',
            first_name='Arc Trooper',
            last_name='Fives'
        )
        fives.set_password('WeAreOneInTheSame')
        fives.save()
        token = log_test_user_in(self, fives, 'WeAreOneInTheSame')

        with self.client:
            resp = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'comments': 'Comments value'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No rating provided.')

    def test_post_feedback_success(self):
        hevy = User(
            email='hevy@arclytics.io',
            first_name='Clone Cadet',
            last_name='Hevy'
        )
        hevy.set_password('WeAreOneInTheSame')
        hevy.save()
        token = log_test_user_in(self, hevy, 'WeAreOneInTheSame')

        with self.client:
            resp = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'rating': 5,
                        'comments': 'Comments value'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], f'Feedback submitted by {hevy.email}.'
            )

            self.assertTrue(Feedback.objects(user=hevy.id))

    def test_ratings_list(self):
        """NOT A REAL UNIT TEST, this is to help me develop the list endpoint"""
        vader = User(
            email='darthvader@arclytics.io',
            first_name='Darth',
            last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_1 = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'rating': 5,
                        'comments': 'Comments value'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_1_1 = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value 2',
                        'rating': 4,
                        'comments': 'Comments value 2'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_1_2 = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value 3',
                        'rating': 3,
                        'comments': 'Comments value 3'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_1_3 = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value 4',
                        'rating': 2,
                        'comments': 'Comments value 4'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_1_4 = self.client.post(
                '/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value 5',
                        'rating': 1,
                        'comments': 'Comments value 5'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_2 = self.client.get(
                '/admin/feedback/list',
                data=json.dumps({'key': 'value'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp_2.data.decode())
            print(data)


if __name__ == '__main__':
    unittest.main()
