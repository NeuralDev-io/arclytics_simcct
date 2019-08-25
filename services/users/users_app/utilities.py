# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""utilities.py: 

{Description}
"""

import datetime
import decimal
import enum
import json
from bson import ObjectId
from datetime import datetime, tzinfo, timedelta
from typing import Optional


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o.isoformat())
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)


class PasswordValidationError(Exception):
    """
    Raises an Exception if now password was set before trying to save
    the User model.
    """
    def __init__(self):
        super(PasswordValidationError,
              self).__init__('A password must be set before saving.')


class ElementSymbolInvalid(Exception):
    """Raises an Exception if the Element does not conform to a valid symbol
    as used in the Periodic Table of Elements.
    """
    default_err = (
        'ValidationError (Element) (Field does not match a valid '
        'element symbol in the Periodic Table: ["symbol"])'
    )

    def __init__(self, message=default_err):
        super(ElementSymbolInvalid, self).__init__(message)


class ElementInvalid(Exception):
    """Raises an Exception if the Element is invalid in any way."""
    prefix = 'ValidationError (Element)'

    def __init__(self, message=''):
        super(ElementInvalid, self).__init__(f'{self.prefix} ({message})')


class MissingElementError(Exception):
    def __init__(self, message=''):
        super(MissingElementError, self).__init__(message)


class SimpleUTC(tzinfo):
    def tzname(self, dt: Optional[datetime]) -> Optional[str]:
        return 'UTC'

    def utcoffset(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)


class PeriodicTable(enum.Enum):
    """An Enum with the Periodic Table element symbol and the atomic number."""
    H = 1
    He = 2
    Li = 3
    Be = 4
    B = 5
    C = 6
    N = 7
    Mg = 12
    Al = 13
    Si = 14
    P = 15
    S = 16
    Cl = 17
    Ar = 18
    K = 19
    Ca = 20
    Sc = 21
    Ti = 22
    V = 23
    Cr = 24
    Mn = 25
    Fe = 26
    Co = 27
    Ni = 28
    Cu = 29
    Zn = 30
    Ga = 31
    Ge = 32
    As = 33
    Se = 34
    Br = 35
    Kr = 36
    Rb = 37
    Sr = 38
    Y = 39
    Zr = 40
    Nb = 41
    Mo = 42
    Tc = 43
    Ru = 44
    Rh = 45
    Pd = 46
    Ag = 47
    Cd = 48
    In = 49
    Sn = 50
    Sb = 51
    Te = 52
    I = 53
    Xe = 54
    Cs = 55
    Ba = 56
    La = 57
    Ce = 58
    Pr = 59
    Nd = 60
    Pm = 61
    Sm = 62
    Eu = 63
    Gd = 64
    Tb = 65
    Dy = 66
    Ho = 67
    Er = 68
    Tm = 69
    Yb = 70
    Lu = 71
    Hf = 72
    Ta = 73
    W = 74
    Re = 75
    Os = 76
    Ir = 77
    Pt = 78
    Au = 79
    Hg = 80
    Tl = 81
    Pb = 82
    Bi = 83
    Po = 84
    At = 85
    Rn = 86
    Fr = 87
    Ra = 88
    Ac = 89
    Th = 90
    Pa = 91
    U = 92
    Np = 93
    Pu = 94
    Am = 95
    Cm = 96
    Bk = 97
    Cf = 98
    Es = 99
    Fm = 100
    Md = 101
    No = 102
    Lr = 103
    Rf = 104
    Db = 105
    Sg = 106
    Bh = 107
    Hs = 108
    Mt = 109
    Ds = 110
    Rg = 111
    Cn = 112
    Nh = 113
    Fl = 114
    Mc = 115
    Lv = 116
    Ts = 117
    Og = 118
