"""The storage module is used to remotely store assets and listings."""
import copy
import hashlib
import json
import jsonld
import signature
import time
import urllib2

def register_asset(config, asset):
    """Digitally signs the given asset and stores it on the listings service.

    config - the configuration to read the private key used for digital 
        signatures from as well as the listings service URL.
    asset - the asset to register in JSON format.

    Returns the digitally signed asset.
    Throws an exception if something nasty happens.
    """
    storage_url = config.get("general", "listings-url") + asset["@"]

    # Fill out the config-based information in the asset copy
    ac = copy.deepcopy(asset)
    
    ac["@"] = "<" + storage_url + ">"
    # FIXME: Need a better way of setting the asset provider. This method
    # is bound to the dev.payswarm.com PaySwarm Authority software.
    ac["ps:assetProvider"] = \
        "<" + config.get("application", 
            "preferences-url").replace("/preferences", "") + ">"
    ac["ps:authority"] = \
        "<" + config.get("general", "config-url") + ">"
    ac["ps:contentUrl"] = \
        "<" + storage_url + ">"

    # Digitally sign the asset
    sa = signature.sign(config, ac)

    # Upload the asset
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(sa, sort_keys = True, indent = 3))
    urllib2.urlopen(req)
    
    return sa

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
    lc = copy.deepcopy(listing)
    asset = copy.deepcopy(signed_asset)
    del asset["sig:signature"]

    lc["@"] = "<" + storage_url + ">"    
    # Set all of the AUTOFILL variables
    if(lc.has_key("com:payee")):
        p = lc["com:payee"]
        p["@"] = "<" + config.get("general", "listings-url") + p["@"] + ">"
        if("AUTOFILL" in p["com:destination"]):
            p["com:destination"] = \
                "<" + config.get("application", "financial-account") + ">"

    # Set the necessary asset/license variables
    lc["ps:asset"] = asset["@"]
    lc["ps:assetHash"] = hashlib.sha1(jsonld.normalize(asset)).hexdigest()
    lc["ps:license"] = \
        "<" + config.get("application", "default-license") + ">"
    lc["ps:licenseHash"] = \
        config.get("application", "default-license-hash")
    lc["ps:validFrom"] = \
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lc["ps:validUntil"] = \
        time.strftime("%Y-%m-%dT%H:%M:%SZ", 
            time.gmtime(time.time() + 60*60*24))

    # Digitally sign the listing
    sl = signature.sign(config, lc)

    # Upload the listing
    req = urllib2.Request(storage_url,
        headers = { "Content-Type": "application/json" },
        data = json.dumps(sl, sort_keys = True, indent = 3))
    urllib2.urlopen(req)

    return sl

