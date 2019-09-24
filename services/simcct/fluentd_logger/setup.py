"""
fluentd_logger
-------------

This library is made to be used as a wrapper with Python's logging library and
to also send logs as events to fluentd with the fluentd-logger library.
"""
from setuptools import setup


setup(
    name='fluentd_logger',
    version='0.3',
    url='',
    license='MIT',
    author='Andrew Che',
    author_email='andrew@codeninja55.me',
    description='Fluentd logging with stdout stream.',
    long_description=__doc__,
    py_modules=['fluentd_logger'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['fluent-logger'],
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
