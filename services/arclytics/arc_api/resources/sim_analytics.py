# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# sim_analytics.py
#
# Attributions:
# [1] van der Maaten, L.J.P.; Hinton, G.E. Visualizing High-Dimensional Data
# Using t-SNE. Journal of Machine Learning Research 9:2579-2605, 2008.
# [2] van der Maaten, L.J.P. t-Distributed Stochastic Neighbor Embedding
# https://lvdmaaten.github.io/tsne/
# [3] L.J.P. van der Maaten. Accelerating t-SNE using Tree-Based Algorithms.
# Journal of Machine Learning Research 15(Oct):3221-3245, 2014.
# https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'development'
__date__ = '2019.10.20'

"""sim_analytics.py:

This module provides the resources for analytical querying, manipulation and
transformations to display interesting data about the simulations and alloys.
"""

from os import environ as env
from typing import Tuple

from flask import Blueprint
from flask_restful import Resource
import pandas as pd

from arc_api.extensions import api
from arc_api.routes import Routes
from arc_api.mongo_service import MongoService
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger
from sklearn.manifold import TSNE

sim_analytics_blueprint = Blueprint('simulation_analytics', __name__)
logger = AppLogger(__name__)

DATABASE = env.get('MONGO_APP_DB')


# noinspection PyMethodMayBeStatic
class SavedAlloysSimilarity(Resource):

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _) -> Tuple[dict, int]:
        """The view method to perform a t-distributed Stochastic Neighbor
        Embedding on the alloy compositions.

        t-SNE [1] is a tool to visualize high-dimensional data. It converts
        similarities between data points to joint probabilities and tries to
        minimize the Kullback-Leibler divergence between the joint
        probabilities of the low-dimensional embedding and the
        high-dimensional data. t-SNE has a cost function that is not convex,
        i.e. with different initializations we can get different results.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """

        # Because our data is stored inside User Documents in the format:
        # [
        #   {
        #       "_id": ObjectId(),
        #       "name": "Alloy name",
        #       "compositions": [
        #           { "symbol": "C", "weight": 0.044 },
        #           { "symbol": "Mn", "weight": 0.021 },
        #           { "symbol": "Fe", "weight": 0.0 },
        #       ]
        #   }
        # ]
        pipeline = [
            # Stage 1 - Unwind the array of saved alloys and project fields we
            # need which will be `_id`, `name`, and `compositions`.
            {'$unwind': '$saved_alloys'},
            {
                '$project': {
                    '_id': 1,
                    'name': '$saved_alloys.name',
                    'compositions': '$saved_alloys.compositions'
                }
            },
            # Stage 2 - Unwind the list of compositions which are element
            # objects and group them by `_id` and `name`
            {'$unwind': '$compositions'},
            {
                '$group': {
                    '_id': {'id': '$_id', 'name': '$name'},
                    'items': {
                        '$addToSet': {
                            'name': '$compositions.symbol',
                            'value': '$compositions.weight'
                        }
                    },
                }
            },
            # Stage 3 - Project the grouped elements which are an array of
            # symbols and weights to a object which does a pivot on the
            # `items.name` and `items.value` where the name because the column
            # and the value becomes the value of that row.
            {
                '$project': {
                    'result': {
                        '$arrayToObject': {
                            '$zip': {'inputs': ["$items.name", "$items.value"]}
                        }
                    }
                }
            },
            # Stage 4 - Add the Alloy name field to the result and change the
            # $$ROOT to be this new `result`.
            {'$addFields': {'result.name': '$_id.name'}},
            {'$replaceRoot': {'newRoot': '$result'}}
        ]

        # Run our querying pipeline and get the result as a `pandas.DataFrame`
        df = MongoService().read_aggregation(
            db_name=DATABASE,
            collection='users',
            pipeline=pipeline
        )

        # Sometimes the list of compositions can have mismatching number of
        # elements (because a user has added an alloy with more elements).
        # In this case, we will have NaN for those lists that don't have those
        # extra elements. We need to fill this with 0.0 as our imputation
        # technique.
        df = df.fillna(0)

        # Separate out the labels of the alloy into a new DataFrame
        labels_df = pd.DataFrame(data=df['name'].values, columns=['name'])
        labels_df.reset_index(drop=True, inplace=True)

        # Separating out the features (i.e. the vector of element weights).
        df.drop(['name'], axis=1, inplace=True)
        X = df.loc[:].values

        # Now we make out t-SNE model using sklearn.
        # sklearn Documentation:
        # https://scikit-learn.org/stable/modules/generated/
        # sklearn.manifold.TSNE.html
        # Args:
        #   n_components: Dimension of the embedded space.
        #   perplexity: The perplexity is related to the number of nearest
        #   neighbors that is used in other manifold learning algorithms.
        #   Larger datasets usually require a larger perplexity. Consider
        #   selecting a value between 5 and 50. Different values can result
        #   in significantly different results.
        #   learning_rate: The learning rate for t-SNE is usually in the
        #   range [10.0, 1000.0]. If the learning rate is too high, the data
        #   may look like a ‘ball’ with any point approximately equidistant
        #   from its nearest neighbours. If the learning rate is too low,
        #   most points may look compressed in a dense cloud with few outliers.
        #   If the cost function gets stuck in a bad local minimum increasing
        #   the learning rate may help.
        #   n_iter: Maximum number of iterations for the optimization. Should
        #   be at least 250.
        tsne_model = TSNE(
            n_components=2, perplexity=35, learning_rate=200., n_iter=350
        )

        # We fit the model to the dataset
        tsne_embedded = tsne_model.fit_transform(X)

        # Create a new aggregated dataframe to store the results
        tsne_df = pd.DataFrame(data=tsne_embedded, columns=['x', 'y'])
        tsne_df.reset_index(drop=True, inplace=True)
        # Join our labels to our 2-dimensional Array
        tsne_df = pd.concat([tsne_df, labels_df], axis=1, ignore_index=True)
        tsne_df.columns = ['x', 'y', 'name']

        # Generate some colour codes
        # Assign each name category a unique code which represents the color
        # of the markers in Plotly.
        tsne_df = tsne_df.assign(
            color=(tsne_df['name']).astype('category').cat.codes
        )

        # View the params used in the model and return that in the response
        params = tsne_model.get_params()

        response = {
            'status': 'success',
            'parameters': params,
            'data': {
                'x': tsne_df['x'].tolist(),
                'y': tsne_df['y'].tolist(),
                'label': tsne_df['name'].tolist(),
                'color': tsne_df['color'].tolist(),
            }
        }
        return response, 200


# noinspection PyMethodMayBeStatic
class MethodCount(Resource):

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _) -> Tuple[dict, int]:
        """The view method to get the count data for the methods used in
        saved simulations.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """
        pipeline = [
            {
                '$project': {
                    '_id': 0,
                    'configs': '$configurations'
                }
            },
            {
                '$group': {
                    '_id': '$configs.method',
                    'count': {'$sum': 1}
                }
            },
        ]

        # Run our querying pipeline and get the result as a `pandas.DataFrame`
        df = MongoService().read_aggregation(
            db_name=DATABASE,
            collection='saved_simulations',
            pipeline=pipeline
        )

        response = {
            'status': 'success',
            'data': {
                'x': df['_id'].tolist(),
                'y': df['count'].tolist()
            }
        }
        return response, 200


# noinspection PyMethodMayBeStatic
class AlloyCountByName(Resource):
    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _) -> Tuple[dict, int]:
        """The view method to get the count data for the alloy by name used in
        saved simulations.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """
        pipeline = [
            {
                '$project': {
                    '_id': 0,
                    'alloy': '$alloy_store.alloys.parent'
                }
            },
            {
                '$group': {
                    '_id': '$alloy.name',
                    'count': {'$sum': 1}
                }
            },
        ]

        # Run our querying pipeline and get the result as a `pandas.DataFrame`
        df = MongoService().read_aggregation(
            db_name=DATABASE,
            collection='saved_simulations',
            pipeline=pipeline
        )

        response = {
            'status': 'success',
            'data': {
                'x': df['count'].tolist(),
                'y': df['_id'].tolist(),
                'colors': [x for x in range(df.shape[0])]
            }
        }
        return response, 200


api.add_resource(MethodCount, Routes.MethodCount.value)
api.add_resource(AlloyCountByName, Routes.AlloyCountByName.value)
api.add_resource(SavedAlloysSimilarity, Routes.SavedAlloysSimilarity.value)
