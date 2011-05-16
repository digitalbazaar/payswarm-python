"""The storage module is used to remotely store assets and listings."""
import copy
import hashlib
import json
import jsonld
import signature
import time
import urllib2

def populate_asset(config, asset):
    """Populates an asset with the provider, authority and content URLs.
    
    config - the configuration to read the asset URLs from.
    asset - the asset to modify.
    
    Returns an updated asset.
    """
    rval = copy.deepcopy(asset)
    storage_url = config.get("general", "listings-url") + asset["@"]
    
    rval["@"] = storage_url
    # FIXME: Need a better way of setting the asset provider. This method
    # is bound to the dev.payswarm.com PaySwarm Authority software.
    rval["ps:assetProvider"] = \
        "<" + config.get("application", 
            "preferences-url").replace("/preferences", "") + ">"
    rval["ps:authority"] = "<" + config.get("general", "config-url") + ">"
    rval["ps:contentUrl"] = "<" + storage_url + ">"

    return rval

def register_asset(config, asset):
    """Digitally signs the given asset and stores it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    asset - the asset to register in JSON format.

    Returns the digitally signed asset.
    Throws an exception if something nasty happens.
    """
    storage_url = config.get("general", "listings-url") + asset["@"]

    # fill out the config-based information in the asset
    populated_asset = populate_asset(config, asset)

    # digitally sign the asset
    sa = signature.sign(config, populated_asset)

    # upload the asset
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(sa, sort_keys = True, indent = 3))
    urllib2.urlopen(req)
    
    return sa

def populate_listing(config, asset, listing):
    """Populates a listing with the asset, license and validity information.
    
    config - the configuration to read the listing data from.
    listing - the listing to modify.
    
    Returns an updated listing.
    """
    rval = copy.deepcopy(listing)
    storage_url = config.get("general", "listings-url") + listing["@"]
    
    rval["@"] = storage_url
    # Set all of the AUTOFILL variables
    if(rval.has_key("com:payee")):
        p = rval["com:payee"]
        p["@"] = config.get("general", "listings-url") + p["@"]
        if("AUTOFILL" in p["com:destination"]):
            p["com:destination"] = \
                "<" + config.get("application", "financial-account") + ">"

    # clear the asset of any signature information
    asset = copy.deepcopy(asset)
    if(asset.has_key("sig:signature")):
        del asset["sig:signature"]

    # Set the necessary asset/license variables
    rval["ps:asset"] = "<" + asset["@"] + ">"
    rval["ps:assetHash"] = hashlib.sha1(jsonld.normalize(asset)).hexdigest()
    rval["ps:license"] = \
        "<" + config.get("application", "default-license") + ">"
    rval["ps:licenseHash"] = \
        config.get("application", "default-license-hash")
    rval["ps:validFrom"] = \
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rval["ps:validUntil"] = \
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
    storage_url = config.get("general", "listings-url") + listing["@"]
    
    # populate the listing
    populated_listing = populate_listing(config, signed_asset, listing)

    # Digitally sign the listing
    sl = signature.sign(config, populated_listing)

    # Upload the listing
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(sl, sort_keys = True, indent = 3))
    urllib2.urlopen(req)

    return sl

