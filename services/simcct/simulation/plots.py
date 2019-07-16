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
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.01'
"""plots.py: 

{Description}
"""


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
            'ferrite_nucleation': ferrite_nucleation,
            'ferrite_completion': ferrite_completion,
            'pearlite_nucleation': pearlite_nucleation,
            'pearlite_completion': pearlite_completion,
            'bainite_nucleation': bainite_nucleation,
            'bainite_completion': bainite_completion,
            'martensite': martensite
        }

    def set_ttt_plot_data(
        self, ferrite_start, ferrite_finish, pearlite_start, pearlite_finish,
        bainite_start, bainite_finish, martensite
    ) -> None:
        self.ttt = {
            'ferrite_start': ferrite_start,
            'ferrite_finish': ferrite_finish,
            'pearlite_start': pearlite_start,
            'pearlite_finish': pearlite_finish,
            'bainite_start': bainite_start,
            'bainite_finish': bainite_finish,
            'martensite': martensite
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
