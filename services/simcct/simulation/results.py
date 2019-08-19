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
__version__ = '0.7.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.01'
"""plots.py: 

{Description}
"""

import csv
import numpy as np
from typing import Union


class Results(object):
    """
    This class is used to store TTT and CCT plotting data. There will also be
    some helper instance methods to allow plotting with Plotly or printing to
    stdout.
    """

    def __init__(self):
        self.ttt = None
        self.cct = None

        self.user_cooling_curve: Union[np.ndarray, None] = None

        self.ttt_fcs: Union[np.ndarray, None] = None
        self.ttt_fcf: Union[np.ndarray, None] = None
        self.ttt_pcs: Union[np.ndarray, None] = None
        self.ttt_pcf: Union[np.ndarray, None] = None
        self.ttt_bcs: Union[np.ndarray, None] = None
        self.ttt_bcf: Union[np.ndarray, None] = None
        self.ttt_msf: Union[np.ndarray, None] = None

        self.cct_fcs: Union[np.ndarray, None] = None
        self.cct_fcf: Union[np.ndarray, None] = None
        self.cct_pcs: Union[np.ndarray, None] = None
        self.cct_pcf: Union[np.ndarray, None] = None
        self.cct_bcs: Union[np.ndarray, None] = None
        self.cct_bcf: Union[np.ndarray, None] = None
        self.cct_msf: Union[np.ndarray, None] = None

    @classmethod
    def from_json(cls):
        pass

    @classmethod
    def from_csv(cls):
        pass

    def set_cct_plot_data(
        self, ferrite_nucleation, ferrite_completion, pearlite_nucleation,
        pearlite_completion, bainite_nucleation, bainite_completion, martensite
    ) -> None:
        self.cct_fcs = ferrite_nucleation
        self.cct_fcf = ferrite_completion
        self.cct_pcs = pearlite_nucleation
        self.cct_pcf = pearlite_completion
        self.cct_bcs = bainite_nucleation
        self.cct_bcf = bainite_completion
        self.cct_msf = martensite

    def set_ttt_plot_data(
        self, ferrite_nucleation, ferrite_completion, pearlite_nucleation,
        pearlite_completion, bainite_nucleation, bainite_completion, martensite
    ) -> None:
        self.ttt_fcs = ferrite_nucleation
        self.ttt_fcf = ferrite_completion
        self.ttt_pcs = pearlite_nucleation
        self.ttt_pcf = pearlite_completion
        self.ttt_bcs = bainite_nucleation
        self.ttt_bcf = bainite_completion
        self.ttt_msf = martensite

    def set_user_cool_plot_data(self, user_cooling_data) -> None:
        self.user_cooling_curve = user_cooling_data

    def get_cct_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': {
                'time': np.trim_zeros(self.cct_fcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_fcs[:, 1]).tolist()
            },
            'ferrite_completion': {
                'time': np.trim_zeros(self.cct_fcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_fcf[:, 1]).tolist()
            },
            'pearlite_nucleation': {
                'time': np.trim_zeros(self.cct_pcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_pcs[:, 1]).tolist()
            },
            'pearlite_completion': {
                'time': np.trim_zeros(self.cct_pcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_pcf[:, 1]).tolist()
            },
            'bainite_nucleation': {
                'time': np.trim_zeros(self.cct_bcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_bcs[:, 1]).tolist()
            },
            'bainite_completion': {
                'time': np.trim_zeros(self.cct_bcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.cct_bcf[:, 1]).tolist()
            },
            'martensite': {
                'time': self.cct_msf[:, 0].tolist(),
                'temp': self.cct_msf[:, 1].tolist()
            }
        }

    def get_ttt_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': {
                'time': np.trim_zeros(self.ttt_fcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_fcs[:, 1]).tolist()
            },
            'ferrite_completion': {
                'time': np.trim_zeros(self.ttt_fcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_fcf[:, 1]).tolist()
            },
            'pearlite_nucleation': {
                'time': np.trim_zeros(self.ttt_pcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_pcs[:, 1]).tolist()
            },
            'pearlite_completion': {
                'time': np.trim_zeros(self.ttt_pcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_pcf[:, 1]).tolist()
            },
            'bainite_nucleation': {
                'time': np.trim_zeros(self.ttt_bcs[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_bcs[:, 1]).tolist()
            },
            'bainite_completion': {
                'time': np.trim_zeros(self.ttt_bcf[:, 0]).tolist(),
                'temp': np.trim_zeros(self.ttt_bcf[:, 1]).tolist()
            },
            'martensite': {
                'time': self.ttt_msf[:, 0].tolist(),
                'temp': self.ttt_msf[:, 1].tolist()
            }
        }

    def get_user_cool_plot_data(self) -> dict:
        return {
            'time': np.trim_zeros(self.user_cooling_curve[:, 0]).tolist(),
            'temp': np.trim_zeros(self.user_cooling_curve[:, 1]).tolist()
        }

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

    def to_csv(self, plot: str = '', path: str = '') -> None:
        ttt_data = zip(
            *[
                self.ttt['ferrite_nucleation']['time'],
                self.ttt['ferrite_nucleation']['temp'],
                self.ttt['ferrite_completion']['time'],
                self.ttt['ferrite_completion']['temp'],
                self.ttt['pearlite_nucleation']['time'],
                self.ttt['pearlite_nucleation']['temp'],
                self.ttt['pearlite_completion']['time'],
                self.ttt['pearlite_completion']['temp'],
                self.ttt['bainite_nucleation']['time'],
                self.ttt['bainite_nucleation']['temp'],
                self.ttt['bainite_completion']['time'],
                self.ttt['bainite_completion']['temp'],
                self.ttt['martensite']['time'],
                self.ttt['martensite']['temp'],
            ]
        )

        cct_data = zip(
            *[
                self.cct['ferrite_nucleation']['time'],
                self.cct['ferrite_nucleation']['temp'],
                self.cct['ferrite_completion']['time'],
                self.cct['ferrite_completion']['temp'],
                self.cct['pearlite_nucleation']['time'],
                self.cct['pearlite_nucleation']['temp'],
                self.cct['pearlite_completion']['time'],
                self.cct['pearlite_completion']['temp'],
                self.cct['bainite_nucleation']['time'],
                self.cct['bainite_nucleation']['temp'],
                self.cct['bainite_completion']['time'],
                self.cct['bainite_completion']['temp'],
                self.cct['martensite']['time'],
                self.cct['martensite']['temp'],
            ]
        )

        with open(path, mode='w') as f:
            writer = csv.writer(f, delimiter=',')

            if plot.lower() == 'ttt' or plot.lower() == 'both':
                # csv export ttt
                writer.writerow(['TTT'])
                writer.writerow(
                    [
                        'ferrite_nucleation', 'ferrite_nucleation',
                        'ferrite_completion', 'ferrite_completion',
                        'pearlite_nucleation', 'pearlite_nucleation',
                        'pearlite_completion', 'pearlite_completion',
                        'bainite_nucleation', 'bainite_nucleation',
                        'bainite_completion', 'bainite_completion',
                        'martensite', 'martensite'
                    ]
                )

                writer.writerow(
                    [
                        'x', 'y', 'x', 'y', 'x', 'y', 'x', 'y', 'x', 'y', 'x',
                        'y', 'x', 'y'
                    ]
                )
                for r in ttt_data:
                    writer.writerow(r)

            if plot.lower() == 'cct' or plot.lower() == 'both':
                # csv export cct
                writer.writerow(['CCT'])
                writer.writerow(
                    [
                        'ferrite_nucleation', 'ferrite_nucleation',
                        'ferrite_completion', 'ferrite_completion',
                        'pearlite_nucleation', 'pearlite_nucleation',
                        'pearlite_completion', 'pearlite_completion',
                        'bainite_nucleation', 'bainite_nucleation',
                        'bainite_completion', 'bainite_completion',
                        'martensite', 'martensite'
                    ]
                )

                writer.writerow(
                    [
                        'x', 'y', 'x', 'y', 'x', 'y', 'x', 'y', 'x', 'y', 'x',
                        'y', 'x', 'y'
                    ]
                )
                for r in cct_data:
                    writer.writerow(r)

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
