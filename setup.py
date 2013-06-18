# -*- coding: utf-8 -*-
"""
PaySwarm
========

A Python_ PaySwarm_ client library.

.. _Python: http://www.python.org/
.. _PaySwarm: http://payswarm.com/
"""

from distutils.core import setup
from pip.req import parse_requirements

with open('README.rst') as file:
    long_description = file.read()

# requirements loading snipit from: http://stackoverflow.com/questions/14399534/how-can-i-reference-requirements-txt-for-the-install-requires-kwarg-in-setuptool/16624700#16624700

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt')

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name = 'PaySwarm',
    version = '0.1.0-dev',
    description = 'Python implementation of the PaySwarm client API',
    long_description=long_description,
    author = 'Digital Bazaar',
    author_email = 'support@digitalbazaar.com',
    url = 'http://github.com/digitalbazaar/payswarm-python',
    packages = ['payswarm'],
    package_dir = {'': 'lib'},
    license = 'BSD 3-Clause license',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=reqs,
)
