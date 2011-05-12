"""The storage module is used to remotely store assets and listings."""
import copy
import json
import jsonld
import urllib2
import signature

def register_asset(config, asset):
    """Digitally signs the given asset and stores it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    asset - the asset to register in JSON format.

    Throws an exception if something nasty happens.
    """
    storage_url = config.get("general", "listings-url") + asset["@"]

    # Fill out the config-based information in the given asset
    signed_asset = copy.deepcopy(asset)

    # Digitally sign the asset

    # Upload the asset
    print storage_url
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(signed_asset, sort_keys = True, indent = 3))
    urllib2.urlopen(req)

def register_listing(config, asset, listing):
    """Digitally signs the given listing, storing it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    asset - the listing to register in JSON format.

    Throws an exception if something nasty happens.
    """
    # Fill out the config-based information in the given listing
    storage_url = config.get("general", "listings-url") + listing["@"]
    signed_listing = copy.deepcopy(listing)

    # Digitally sign the listing

    # Upload the listing
    print storage_url
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(signed_listing, sort_keys = True, indent = 3))
    urllib2.urlopen(req)

