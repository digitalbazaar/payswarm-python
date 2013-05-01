Introduction
------------

A Python implementation of a PaySwarm client. The client is capable of
registering with a PaySwarm Authority, generating public/private keys,
digitally signing and registering assets for sale, registering listings,
establishing Payment Sessions and performing purchases.

Requirements
------------

 * python (2.5 or later)
 * python-m2crypto (0.20.1 or later)

Usage
-----

To configure a PaySwarm client run the following command:

./payswarm config

To register a listing:

./payswarm register listings/test.json

To perform a purchase of the listing:

./payswarm purchase listings/test.json

Once you purchase a listing, future purchases of that listing will not
charge you any money. You may re-purchase the item by re-registering
the asset and listing, which will force a new digital signature on the 
items, thus allowing you to purchase the newly registered item.





