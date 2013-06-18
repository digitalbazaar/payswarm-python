payswarm-python
===============

Introduction
------------

This is a Python_ implementation of a PaySwarm_ client. Some features of this client:

- Generating and public/private key pairs.
- Registering public keys with a PaySwarm Authority.
- Digitally signing and verifying JSON-LD_ data such as assets and listings.
- Registering assets for sale.
- Registering listings.
- Performing purchases.

You may also be interested in the similar JavaScript project. It includes a
node.js_ based command line client with addtional features:

- https://github.com/digitalbazaar/payswarm.js

Requirements
------------

- Python_ (>= 2.5)
- PyCrypto_ (>= 2.6)
- PyLD_ (>= 0.1.0)
- argparse_ (>= 1.2.1)
- urllib3_ (>= 1.6)
- ndg-httpsclient_ (>= 0.3.2)
- pyOpenSSL_ (>= 0.13)
- pyasn1_ (>= 0.1.7)

urllib3_ is used by default instead of standard modules due to the Python_ 2.x
series not supporting SNI_. The SNI_ support in urllib3_ requires pyOpenSSL_,
ndg-httpsclient_, and pyasn1_. The code will fallback to using ``urllib2`` if
urllib3 is not available but be aware that SNI_ support will silently be absent
which can cause confusing errors when fetching network resources.

Test Requirements
-----------------

Tests can be run with the standard ``unittest`` module or nose_. Coverage
testing requires nose_ and coverage_.

- coverage_ (> 3.6)
- nose_ (>= 1.3.0)

Installation
------------

The easiest installation method is to use ``pip``::

    pip install payswarm

To install testing requirements::

    pip install -r test-requirements.txt

Usage
-----

To configure a PaySwarm client run the following command:

::
    ./payswarm config

To register a listing:

::
    ./payswarm register listings/test.json

To perform a purchase of the listing:

::
    ./payswarm purchase listings/test.json

Once you purchase a listing, future purchases of that listing will not
charge you any money. You may re-purchase the item by re-registering the
asset and listing, which will force a new digital signature on the items,
thus allowing you to purchase the newly registered item.

Testing
-------

Testing with nose_::

    make test

Coverage testing with nose_ and coverage_ with results in ./cover/::

    make cover

Testing with standard ``unittest`` module::

    make unittest-test

Cleaning up coverage output::

    make clean


Authors
-------

This software was written by `Digital Bazaar`_ and friends. Please see the
AUTHORS_ file for full credits.

License
-------

Please see the LICENSE_ file for full license details.

.. _PaySwarm: http://payswarm.com/
.. _Digital Bazaar: http://digitalbazaar.com/
.. _JSON-LD: http://json-ld.org/
.. _node.js: http://nodejs.org/
.. _SNI: http://en.wikipedia.org/wiki/Server_Name_Indication
.. _AUTHORS: AUTHORS
.. _LICENSE: LICENSE

.. _Python: http://www.python.org/

.. _PyCrypto: http://www.pycrypto.org/
.. _PyLD: https://pypi.python.org/pypi/PyLD
.. _argparse: https://pypi.python.org/pypi/argparse
.. _coverage: https://pypi.python.org/pypi/coverage
.. _ndg-httpsclient: https://pypi.python.org/pypi/ndg-httpsclient
.. _nose: https://pypi.python.org/pypi/nose/
.. _pyOpenSSL:  https://pypi.python.org/pypi/pyOpenSSL
.. _pyasn1: https://pypi.python.org/pypi/pyasn1
.. _urllib3: https://pypi.python.org/pypi/urllib3
