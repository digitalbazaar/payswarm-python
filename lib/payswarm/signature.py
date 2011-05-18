"""The signature module is used to perform PaySwarm signatures on data."""
import base64
import binascii
import copy
import hashlib
import json
import jsonld
import M2Crypto
import time

def sign(config, item):
    """Performs a digital signature on a given item.

    config - the configuration to use when reading the private key data.
    item - the associative array to digitally sign.

    Returns a modified item which contains the digital signature information.
    """
    rval = copy.deepcopy(item)
    
    # Generate the signature creation time
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # generate the signature
    #print "PRE-SIG ITEM:\n", jsonld.normalize(rval)
    #print "PRE-SIG SHA1:", hashlib.sha1(jsonld.normalize(rval)).hexdigest()

    # normalize the item to be signed
    normalized = jsonld.normalize(item)
    
    # load the key from the config
    private_pem = config.get("application", "private-key")
    private_key = M2Crypto.EVP.load_key_string(private_pem)
    
    # perform the signature
    private_key.reset_context(md='sha1')
    private_key.sign_init()
    private_key.sign_update(normalized)
    sig_bytes = private_key.sign_final()
    signature = binascii.b2a_base64(sig_bytes).strip()

    rval["sig:signature"] = \
    {
        "a": "sig:JsonldSignature",
        "dc:created": created,
        "dc:creator": config.get("application", "public-key-url"),
        "sig:signatureValue": signature,
    }

    #print "POST-SIG ITEM:\n", jsonld.normalize(rval)
    #print "POST-SIG SHA1:", hashlib.sha1(jsonld.normalize(rval)).hexdigest()
    
    return rval

