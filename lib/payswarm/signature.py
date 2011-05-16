"""The signature module is used to perform PaySwarm signatures on data."""
import Crypto.PublicKey.RSA as RSA
from Crypto.Util.number import long_to_bytes
import base64
import binascii
import copy
import hashlib
import json
import jsonld
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

    # Generate the signature    
    sha1 = hashlib.sha1(jsonld.normalize(item)).hexdigest()
    key = RSA.importKey(config.get("application", "private-key"))
    sig_bytes = long_to_bytes(key.sign(sha1, '')[0])
    signature = binascii.b2a_base64(sig_bytes).strip()

    rval["sig:signature"] = \
    {
        "a": "sig:JsonldSignature",
        "dc:created": created,
        "dc:creator": "<" + config.get("application", "public-key-url") + ">",
        "sig:signatureValue": signature,
    }
    
    return rval

