# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.25'
"""utilities.py: 

Utilities for extensions that are not clearly defined.
"""

import decimal
import enum
import json
import os
from datetime import datetime, timedelta, tzinfo
from typing import Optional

import numpy as np
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError

from simulation.utilities import Method


def get_mongo_uri():
    host = os.environ.get('MONGO_HOST')
    port = int(os.environ.get('MONGO_PORT'))
    db = str(os.environ.get('MONGO_APP_DB'))
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        username = str(os.environ.get('MONGO_APP_USER'))
        password = str(os.environ.get('MONGO_APP_USER_PASSWORD'))
        return f'mongodb://{username}:{password}@{host}:{port}/{db}'
    else:
        return f'mongodb://{host}:{port}/{db}'


# Note: This is not being used anymore as the CORS package is automatically
# setting these headers as we defined them in `sim_api.app.py`. These headers
# are crucially necessary for the Cookies and Server-Side Sessions to work.
RESPONSE_HEADERS = {
    'Access-Control-Allow-Headers':
    'Content-Type',
    'Content-Type':
    'application/json',
    'Access-Control-Allow-Credentials':
    'true',
    'Access-Control-Expose-Headers':
    ['Access-Control-Allow-Credentials', 'Access-Control-Allow-Origin'],
    'Vary':
    'Origin'
    # 'Access-Control-Allow-Origin': '*',  # Don't set this because it fails
    # Reason being that allow from all origins with
    # `'Access-Control-Allow-Credentials': 'true'` will raise an error from
    # the client-side browser.
}


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""
    def default(self, o):
        if isinstance(o, Method):
            return o.name
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, datetime):
            return str(o.isoformat())
        if isinstance(o, np.float):
            return str(o)
        if isinstance(o, np.float32):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
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


class URLTokenError(Exception):
    """
    A custom exception to be raised from any itsdangerous package exceptions.
    """
    def __init__(self, msg: str = None):
        super(URLTokenError, self).__init__(msg)


class URLTokenExpired(Exception):
    """
    Custom exception to be raised from any `itsdangerous` package exceptions.
    """
    def __init__(self, msg: str = None):
        super(URLTokenExpired, self).__init__(msg)


def arc_validate_email(email: str) -> dict:
    """
    Custom email validator that uses the email-validator library.
    """
    # Check for the arclytics.io domain
    if isinstance(email, str):
        # First split the email into username and domain
        email_split = email.split('@')
        # Ensure both keys are present
        if len(email_split) == 2:
            # Check the domain
            if email_split[1] == 'arclytics.io':
                return {
                    'msg': 'Email has arclytics.io as the domain.',
                    'email': email
                }
    # Otherwise we validate normally. `validate_email` will raise
    # EmailNotValidError if the email is invalid.
    valid_email_dict = validate_email(email)
    return valid_email_dict


class ElementSymbolInvalid(Exception):
    """
    Raises an Exception if the Element does not conform to a valid symbol
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


class ElementWeightInvalid(Exception):
    """Raises an Exception if the Element is invalid in any way."""
    prefix = 'ValidationError (Weight)'

    def __init__(self, message=''):
        super(ElementWeightInvalid,
              self).__init__(f'{self.prefix} ({message})')


class MissingElementError(Exception):
    def __init__(self, message=''):
        super(MissingElementError, self).__init__(message)


class DuplicateElementError(Exception):
    """
    Raises an Exception if there is a duplicate element in an alloy, i.e. there
    are two or more elements in an alloy with the same symbol.
    """

    default_err = (
        'ValidationError (Alloy) (Alloy cannot have multiple elements with the'
        'chemical symbol)'
    )

    def __init(self, message=default_err):
        super(DuplicateElementError, self).__init__(message)


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
