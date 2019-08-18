# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# plots.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.7/.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.01'
"""plots.py: 

{Description}
"""

from numpy import trim_zeros


class Plots(object):
    """
    This class is used to store TTT and CCT plotting data. There will also be some helper instance methods
    to allow plotting with Plotly or printing to stdout.
    """

    def __init__(self):
        self.ttt = None
        self.cct = None

    @classmethod
    def from_json(cls):
        pass

    @classmethod
    def from_csv(cls):
        pass

    @classmethod
    def from_pickle(cls):
        pass

    def set_cct_plot_data(
        self, ferrite_nucleation, ferrite_completion, pearlite_nucleation,
        pearlite_completion, bainite_nucleation, bainite_completion, martensite
    ) -> None:
        self.cct = {
            'ferrite_nucleation': {
                'time': ferrite_nucleation[:, 0].tolist(),
                'temp': ferrite_nucleation[:, 1].tolist()
            },
            'ferrite_completion': {
                'time': ferrite_completion[:, 0].tolist(),
                'temp': ferrite_completion[:, 1].tolist()
            },
            'pearlite_nucleation': {
                'time': pearlite_nucleation[:, 0].tolist(),
                'temp': pearlite_nucleation[:, 1].tolist()
            },
            'pearlite_completion': {
                'time': pearlite_completion[:, 0].tolist(),
                'temp': pearlite_completion[:, 1].tolist()
            },
            'bainite_nucleation': {
                'time': bainite_nucleation[:, 0].tolist(),
                'temp': bainite_nucleation[:, 1].tolist()
            },
            'bainite_completion': {
                'time': bainite_completion[:, 0].tolist(),
                'temp': bainite_completion[:, 1].tolist()
            },
            'martensite': {
                'time': martensite[:, 0].tolist(),
                'temp': martensite[:, 1].tolist()
            }
        }

    def set_ttt_plot_data(
        self, ferrite_start, ferrite_finish, pearlite_start, pearlite_finish,
        bainite_start, bainite_finish, martensite
    ) -> None:
        self.ttt = {
            'ferrite_start': {
                'time': ferrite_start[:, 0].tolist(),
                'temp': ferrite_start[:, 1].tolist()
            },
            'ferrite_finish': {
                'time': ferrite_finish[:, 0].tolist(),
                'temp': ferrite_finish[:, 1].tolist()
            },
            'pearlite_start': {
                'time': pearlite_start[:, 0].tolist(),
                'temp': pearlite_start[:, 1].tolist()
            },
            'pearlite_finish': {
                'time': pearlite_finish[:, 0].tolist(),
                'temp': pearlite_finish[:, 1].tolist()
            },
            'bainite_start': {
                'time': bainite_start[:, 0].tolist(),
                'temp': bainite_start[:, 1].tolist()
            },
            'bainite_finish': {
                'time': bainite_finish[:, 0].tolist(),
                'temp': bainite_finish[:, 1].tolist()
            },
            'martensite': {
                'time': martensite[:, 0].tolist(),
                'temp': martensite[:, 1].tolist()
            }
        }

    def get_cct_plot_data(self) -> dict:
        return self.cct

    def get_ttt_plot_data(self) -> dict:
        return self.ttt

    def plot_cct(self):
        # plot with plotly
        pass

    def plot_ttt(self):
        # plot with plotly
        pass

    @staticmethod
    def to_json(data: dict):
        pass

    @staticmethod
    def to_string(plot: str = ''):
        if plot.lower() == 'cct':
            # stringify cct
            return 'cct'
        elif plot.lower() == 'ttt':
            # stringify ttt
            return 'ttt'

        return 'Error'

    @staticmethod
    def to_csv(plot: str = '', path: str = '') -> None:
        if plot.lower() == 'cct':
            # csv export cct
            pass
        elif plot.lower() == 'ttt':
            # csv export ttt
            pass

    @staticmethod
    def to_pickle(plot: str = '', path: str = ''):
        if plot.lower() == 'cct':
            # pickle export cct
            pass
        elif plot.lower() == 'ttt':
            # pickle export ttt
            pass

    def __str__(self):
        # print something else other than data
        pass
