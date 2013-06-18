payswarm-python
===============

**NOTE**: This PaySwarm Python code is very outdated as of May 2013.  Help
updating the code is always welcome! Until it is updated please see the
similar JavaScript based project:

- https://github.com/digitalbazaar/payswarm.js

Introduction
------------

This is a Python_ implementation of a PaySwarm_ client. The client is
capable of registering with a PaySwarm Authority, generating public/private
keys, digitally signing and registering assets for sale, registering
listings, establishing Payment Sessions and performing purchases.

Requirements
------------

- Python_ (2.5 or later)
- PyCrypto_ (2.6 or later)

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

Authors
-------

This software was written by `Digital Bazaar`_ and friends. Please see the
AUTHORS_ file for full credits.

License
-------

Please see the LICENSE_ file for full license details.

.. _PaySwarm: http://payswarm.com/
.. _Digital Bazaar: http://digitalbazaar.com/
.. _Python: http://www.python.org/
.. _PyCrypto: http://www.pycrypto.org/
.. _AUTHORS: AUTHORS
.. _LICENSE: LICENSE