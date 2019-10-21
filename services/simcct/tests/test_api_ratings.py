# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_ratings.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.08.27'

import json
import os
import unittest
from pathlib import Path

from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.models import AdminProfile, Feedback, User
from tests.test_api_base import BaseTestCase
from tests.test_utilities import test_login

logger = AppLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'feedback.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    _TEST_JSON = json.load(f)


def load_test_feedback(self, user: User):
    for f in _TEST_JSON:
        f['user'] = user.id
        feedback = Feedback(**f)
        feedback.save()
    return


class TestRatingsService(BaseTestCase):
    """Tests for Ratings and feedback endpoints"""
    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()
        db.feedback.drop()

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()
        db.feedback.drop()

    def test_post_rating_no_data(self):
        mace = User(
            **{
                'email': 'mace@arclytics.io',
                'first_name': 'Mace',
                'last_name': 'Windu'
            }
        )
        mace.set_password('ThisPartysOver')
        mace.save()

        with self.client as client:
            test_login(client, mace.email, 'ThisPartysOver')
            resp = client.post(
                '/v1/sim/user/rating',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_post_rating_no_rating(self):
        plo = User(
            **{
                'email': 'plokoon@arclytics.io',
                'first_name': 'Plo',
                'last_name': 'Koon'
            }
        )
        plo.set_password('WhenYouAskForTrouble')
        plo.save()

        with self.client as client:
            test_login(client, plo.email, 'WhenYouAskForTrouble')
            resp = client.post(
                '/v1/sim/user/rating',
                data=json.dumps({'invalid_key': 'some_value'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No rating provided.')

    def test_post_rating_invalid_rating(self):
        jhonny = User(
            **{
                'email': 'jhonny@arclytics.io',
                'first_name': 'Jhonny',
                'last_name': 'Koon'
            }
        )
        jhonny.set_password('WhenYouAskForTrouble')
        jhonny.save()

        with self.client as client:
            test_login(client, jhonny.email, 'WhenYouAskForTrouble')
            resp = client.post(
                '/v1/sim/user/rating',
                data=json.dumps({'rating': '3.5'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Rating validation error.')

    def test_post_rating_success(self):
        rex = User(
            **{
                'email': 'rex@arclytics.io',
                'first_name': 'Captain',
                'last_name': 'Rex'
            }
        )
        rex.set_password('ExperienceOutranksEverything')
        rex.save()

        with self.client as client:
            test_login(client, rex.email, 'ExperienceOutranksEverything')
            resp = client.post(
                '/v1/sim/user/rating',
                data=json.dumps({'rating': '5'}),
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
            **{
                'email': 'cody@arclytics.io',
                'first_name': 'Commander',
                'last_name': 'Cody'
            }
        )
        cody.set_password('BlastHim')
        cody.save()

        with self.client as client:
            test_login(client, cody.email, 'BlastHim')
        resp_1 = client.post(
            '/v1/sim/user/rating',
            data=json.dumps({'rating': '3'}),
            content_type='application/json'
        )
        resp_2 = client.post(
            '/v1/sim/user/rating',
            data=json.dumps({'rating': '5'}),
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
            **{
                'email': 'echo@arclytics.io',
                'first_name': 'Arc Trooper',
                'last_name': 'Echo'
            }
        )
        echo.set_password('WeGotToFollowOrders')
        echo.save()

        with self.client as client:
            test_login(client, echo.email, 'WeGotToFollowOrders')
            resp = client.post(
                '/v1/sim/user/feedback',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_post_feedback_missing_fields(self):
        fives = User(
            **{
                'email': 'fives@arclytics.io',
                'first_name': 'Arc Trooper',
                'last_name': 'Fives'
            }
        )
        fives.set_password('WeAreOneAndTheSame')
        fives.save()

        with self.client as client:
            test_login(client, fives.email, 'WeAreOneAndTheSame')
            resp = client.post(
                '/v1/sim/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'comments': 'Comments value'
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No comment provided.')

    def test_post_feedback_validation_error(self):
        hevy = User(
            **{
                'email': 'hevy@arclytics.io',
                'first_name': 'Clone Cadet',
                'last_name': 'Hevy'
            }
        )
        hevy.set_password('YouDeserveIt')
        hevy.save()

        with self.client as client:
            test_login(client, hevy.email, 'YouDeserveIt')
            resp = client.post(
                '/v1/sim/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'rating': 9000,
                        'comment': 'Comments value'
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Feedback validation error.')

    def test_post_feedback_success(self):
        hevy = User(
            **{
                'email': 'cadet-hevy@arclytics.io',
                'first_name': 'Clone Cadet',
                'last_name': 'Hevy'
            }
        )
        hevy.set_password('YouDeserveIt')
        hevy.save()

        with self.client as client:
            test_login(client, hevy.email, 'YouDeserveIt')
            resp = client.post(
                '/v1/sim/user/feedback',
                data=json.dumps(
                    {
                        'category': 'Category value',
                        'rating': 5,
                        'comment': 'Comments value'
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], f'Feedback submitted by {hevy.email}.'
            )

            # self.assertTrue(Feedback.objects(user=hevy.id))

    def test_get_feedback_list_invalid_sort(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'sort_on': 'invalid_category_value'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Sort value is invalid.')

    def test_get_feedback_list_invalid_limit(self):
        vader = User(
            **{
                'email': 'doarthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'limit': 'invalid_limit_value'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Limit value is invalid.')

    def test_get_feedback_list_limit_less_than_one(self):
        vader = User(
            **{
                'email': 'darthevader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'limit': -1}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Limit must be > 1.')

    def test_get_feedback_list_invalid_offset(self):
        vader = User(
            **{
                'email': 'dartfhvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'offset': 'invalid_offset_value'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Offset value is invalid.')

    def test_get_feedback_list_offset_too_large(self):
        vader = User(
            **{
                'email': 'darwdthqvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'offset': 100}),
                content_type='application/json'
            )
            logger.debug(resp.data.decode())
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Offset value exceeds number of records.'
            )

    def test_get_feedback_list_offset_less_than_one(self):
        vader = User(
            **{
                'email': 'darsthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        load_test_feedback(self, vader)

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({'offset': -1}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Offset must be > 1.')

    def test_get_feedback_list_success(self):
        vader = User(
            email='darrthvoader@arclytics.io',
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

        load_test_feedback(self, vader)

        with self.client:
            test_login(self.client, vader.email, 'AllTooEasy')
            resp_1 = self.client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps({
                    'limit': 4,
                    'sort_on': 'rating'
                }),
                content_type='application/json'
            )
            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')
            self.assertEqual(data_1['sort_on'], 'rating')
            self.assertEqual(data_1['next_offset'], 5)
            self.assertEqual(data_1['prev_offset'], None)
            self.assertEqual(data_1['limit'], 4)
            self.assertEqual(data_1['current_page'], 1)
            self.assertEqual(data_1['total_pages'], 3)

            resp_2 = self.client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps(
                    {
                        'offset': 5,
                        'limit': 4,
                        'sort_on': 'rating'
                    }
                ),
                content_type='application/json'
            )

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')
            self.assertEqual(data_2['sort_on'], 'rating')
            self.assertEqual(data_2['next_offset'], 9)
            self.assertEqual(data_2['prev_offset'], 1)
            self.assertEqual(data_2['limit'], 4)
            self.assertEqual(data_2['current_page'], 2)
            self.assertEqual(data_2['total_pages'], 3)

            resp_3 = self.client.get(
                '/v1/sim/admin/feedback/list',
                data=json.dumps(
                    {
                        'offset': 9,
                        'limit': 4,
                        'sort_on': 'rating'
                    }
                ),
                content_type='application/json'
            )

            data_3 = json.loads(resp_3.data.decode())
            self.assertEqual(resp_3.status_code, 200)
            self.assertEqual(data_3['status'], 'success')
            self.assertEqual(data_3['sort_on'], 'rating')
            self.assertEqual(data_3['next_offset'], None)
            self.assertEqual(data_3['prev_offset'], 5)
            self.assertEqual(data_3['limit'], 4)
            self.assertEqual(data_3['current_page'], 3)
            self.assertEqual(data_3['total_pages'], 3)

    def test_post_subscribe_already_subscribed(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None,
            sub_to_feedback=True
        )
        vader.save()

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = self.client.post(
                '/v1/sim/admin/feedback/list/subscribe',
                data=json.dumps({'action': 'subscribe'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User is already subscribed.')

    def test_post_unsubscribe_already_unsubscribed(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None,
            sub_to_feedback=False
        )
        vader.save()

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = self.client.post(
                '/v1/sim/admin/feedback/list/subscribe',
                data=json.dumps({'action': 'unsubscribe'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User is already unsubscribed.')

    def test_post_subscribe_success(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None,
            sub_to_feedback=False
        )
        vader.save()

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = self.client.post(
                '/v1/sim/admin/feedback/list/subscribe',
                data=json.dumps({'action': 'subscribe'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'User has been subscribed.')

            vader_updated = User.objects.get(email=vader.email)
            self.assertEqual(
                vader_updated['admin_profile']['sub_to_feedback'], True
            )

    def test_post_unsubscribe_success(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None,
            sub_to_feedback=True
        )
        vader.save()

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')
            resp = self.client.post(
                '/v1/sim/admin/feedback/list/subscribe',
                data=json.dumps({'action': 'unsubscribe'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'User has been unsubscribed.')

            vader_updated = User.objects.get(email=vader.email)
            self.assertEqual(
                vader_updated['admin_profile']['sub_to_feedback'], False
            )


if __name__ == '__main__':
    unittest.main()
