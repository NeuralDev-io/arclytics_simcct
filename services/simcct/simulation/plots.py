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


class Plots(object):
    """
    This class is used to store TTT and CCT plotting data. There will also be
    some helper instance methods to allow plotting with Plotly or printing to
    stdout.
    """

    def __init__(self):
        self.ttt = None
        self.cct = None

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
        self.ttt_fcs = ferrite_start
        self.ttt_fcf = ferrite_finish
        self.ttt_pcs = pearlite_start
        self.ttt_pcf = pearlite_finish
        self.ttt_bcs = bainite_start
        self.ttt_bcf = bainite_finish
        self.ttt_msf = martensite

    def get_cct_plot_data(self) -> dict:
        # TODO(andrew@neuraldev.io): Need to trim these lists.
        return self.cct

    def get_ttt_plot_data(self) -> dict:
        # ferrite_nucleation_x = []
        # ferrite_nucleation_y = []
        #
        # for i, v in enumerate(self.ttt_fcs[:, 0]):
        #     if self.ttt_fcs[i, 0] > 0:
        #         ferrite_nucleation_x.append(self.ttt_fcs[i, 0])
        #         ferrite_nucleation_y.append(self.ttt_fcs[i, 1])
        #
        # ferrite_completion_x = []
        # ferrite_completion_y = []
        #
        # for i, v in enumerate(self.ttt_fcf[:, 0]):
        #     if self.ttt_fcf[i, 0] > 0:
        #         ferrite_completion_x.append(self.ttt_fcf[i, 0])
        #         ferrite_completion_y.append(self.ttt_fcf[i, 1])

        # TODO(andrew@neuraldev.io): Need to trim these lists.
        ttt = {
            'ferrite_nucleation': {
                'time': self.ttt_fcs[:, 0].tolist(),
                'temp': self.ttt_fcs[:, 1].tolist()
            },
            'ferrite_completion': {
                'time': self.ttt_fcf[:, 0].tolist(),
                'temp': self.ttt_fcf[:, 1].tolist()
            },
            'pearlite_nucleation': {
                'time': self.ttt_pcs[:, 0].tolist(),
                'temp': self.ttt_pcs[:, 1].tolist()
            },
            'pearlite_completion': {
                'time': self.ttt_pcf[:, 0].tolist(),
                'temp': self.ttt_pcf[:, 1].tolist()
            },
            'bainite_nucleation': {
                'time': self.ttt_bcs[:, 0].tolist(),
                'temp': self.ttt_bcs[:, 1].tolist()
            },
            'bainite_completion': {
                'time': self.ttt_bcf[:, 0].tolist(),
                'temp': self.ttt_bcf[:, 1].tolist()
            },
            'martensite': {
                'time': self.ttt_msf[:, 0].tolist(),
                'temp': self.ttt_msf[:, 1].tolist()
            }
        }

        return ttt

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
