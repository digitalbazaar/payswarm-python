"""The storage plugin is used to remotely store assets and listings."""
import copy
import hashlib
import json
import os
import time
import urllib2

import pyld.jsonld as jsonld

import constants
import signature
import util


def populate_asset(config, asset):
    """Populates an asset with the provider, authority and content URLs.
    
    config - the configuration to read the asset URLs from.
    asset - the asset to modify.
    
    Returns an updated asset.
    """
    rval = copy.deepcopy(asset)
    storage_url = config.get("general", "listings-url") + asset["id"]
    
    rval["id"] = storage_url
    # FIXME: Need a better way of setting the asset provider. This method
    # is bound to the dev.payswarm.com PaySwarm Authority software.
    rval["assetProvider"] = \
        config.get("application", 
            "preferences-url").replace("/preferences", "")
    rval["authority"] = config.get("general", "config-url")
    rval["contentUrl"] = storage_url

    return rval

def register_asset(config, asset):
    """Digitally signs the given asset and stores it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    asset - the asset to register in JSON format.

    Returns the digitally signed asset.
    Throws an exception if something nasty happens.
    """
    storage_url = config.get("general", "listings-url") + asset["id"]

    # fill out the config-based information in the asset
    populated_asset = populate_asset(config, asset)

    # include the default context if necessary
    populated_asset.setdefault("@context", constants.CONTEXT)

    # digitally sign the asset
    sa = signature.sign(config, populated_asset)

    # upload the asset
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/ld+json" },
        data = json.dumps(sa, sort_keys=True, indent=3))
    urllib2.urlopen(req)
    
    return sa

def fetch(config, item):
    """Fetches the given item from the Listings service URL.
    
    config - the configuration to read the listing data from.
    item - an object containing a '@' key, which will be combined with the
        listings-url to create a URL. That URL will be used to fetch the
        item.
    """
    rval = None
    storage_url = config.get("general", "listings-url") + item["id"]

    # retrieve the listing
    rval = json.loads(urllib2.urlopen(storage_url).read())

    return rval

def populate_listing(config, asset, listing):
    """Populates a listing with the asset, license and validity information.
    
    config - the configuration to read the listing data from.
    listing - the listing to modify.
    
    Returns an updated listing.
    """
    rval = copy.deepcopy(listing)
    storage_url = config.get("general", "listings-url") + listing["id"]
    
    rval["id"] = storage_url
    # Set all of the AUTOFILL variables
    if(rval.has_key("com:payee")):
        p = rval["com:payee"]
        p["id"] = config.get("general", "listings-url") + p["id"]
        if("AUTOFILL" in p["com:destination"]):
            p["com:destination"] = \
                config.get("application", "financial-account")

    # Set the necessary asset/license variables
    rval["asset"] = asset["id"]
    rval["assetHash"] = util.hash(asset)
    rval["license"] = \
        config.get("application", "default-license")
    rval["licenseHash"] = \
        config.get("application", "default-license-hash")
    rval["validFrom"] = \
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rval["validUntil"] = \
        time.strftime("%Y-%m-%dT%H:%M:%SZ", 
            time.gmtime(time.time() + 60*60*24))

    return rval

def register_listing(config, signed_asset, listing):
    """Digitally signs the given listing, storing it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    signed_asset - the digitally signed asset that is a part of the
        listing.
    listing - the listing to register in JSON format.

    Returns the signed listing.
    Throws an exception if something nasty happens.
    """
    # Fill out the config-based information in the given listing
    storage_url = config.get("general", "listings-url") + listing["id"]
    
    # populate the listing
    populated_listing = populate_listing(config, signed_asset, listing)

    # include the default context if necessary
    populated_listing.setdefault("@context", constants.CONTEXT)

    # Digitally sign the listing
    sl = signature.sign(config, populated_listing)

    # Upload the listing
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/ld+json" },
        data = json.dumps(sl, sort_keys=True, indent=2))
    urllib2.urlopen(req)

    return sl


class Storage(util.Plugin):
    """Plugin to publish PaySwarm assets and listings."""

    def __init__(self):
        pass

    def get_name(self):
        return "Storage"

    def before_args_parsed(self, parser, subparsers):
        pass

    def after_args_parsed(self, args):
        pass

    def run(self, args):
        pass

