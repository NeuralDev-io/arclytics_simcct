"""
Flask-Fluentd-Logger
-------------

This library is made to be used as a wrapper with Python's logging library and
to also send logs as events to fluentd with the fluentd-logger library.
"""
from setuptools import setup


setup(
    name='flask_fluentd_logger',
    version='0.1',
    url='https://github.com/codeninja55/flask-fluentd-logger',
    license='MIT',
    author='Andrew Che',
    author_email='andrew@codeninja55.me',
    description='Flask fluentd logging with stdout stream.',
    long_description=__doc__,
    py_modules=['flask_fluentd_logger'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'fluent-logger',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Logging :: fluentd',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
