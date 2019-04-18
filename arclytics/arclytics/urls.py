# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_simcct_api
# urls.py
#
# Attributions:
# [1] https://www.django-rest-framework.org/tutorial/quickstart/
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.04.06'

"""urls.py: 

{Description}
"""

from django.urls import include, path
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]