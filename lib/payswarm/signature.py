"""The signature module is used to perform PaySwarm signatures on data."""

# Copyright (c) 2011-2013, Digital Bazaar, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Digital Bazaar, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import copy
import datetime
import json

have_urllib3 = False
try:
    # NOTE: Using urllib3 since urllib2 does not support SNI.
    # SNI support also requires:
    #   'pyOpenSSL', 'ndg-httpsclient', and 'pyasn1'
    import urllib3
    # setup to get SNI support
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
    # create a shared pool
    urllib3pool = urllib3.PoolManager()
    have_urllib3 = True
except ImportError:
    import urllib2

import payswarm

# W3C date format
W3C_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def sign(jsonld, public_key_id, private_key_pem, nonce=None, created=None):
    """Adds a digital signature to an object.

    jsonld - the JSON-LD to digitally sign.
    public_key_id - the public key id to sign with.
    private_key_pem - the private key in PEM-encoded format.
    nonce - the nonce to use (optional).
    created - the signature creation date and time as either a W3C formatted dateTime or a datetime
        object.
    """

    jsonld = copy.deepcopy(jsonld)

    # Generate the signature creation time as string
    created = created or datetime.datetime.utcnow()
    if isinstance(created, datetime.datetime):
        created = created.strftime(W3C_DATE_FORMAT)

    # normalize the data to be signed
    normalized = payswarm.jsonld.normalize(jsonld, {
        'format': 'application/nquads'
    })

    if len(normalized) == 0:
        raise Exception('Attempt to sign empty normalized data.')

    # load the key
    private_key = RSA.importKey(private_key_pem)

    # build the hash
    h = SHA256.new()
    if nonce:
        h.update(nonce)
    h.update(created)
    h.update(normalized)

    # create the signature
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(h)

    # add signature
    jsonld['signature'] = \
    {
        'type': 'GraphSignature2012',
        'creator': public_key_id,
        'created': created,
        'signatureValue': signature.encode('base64'),
    }
    if nonce:
        obj['signature'] = nonce

    return jsonld


def verify(jsonld):
    """Verifies a digital signature in an object.

    jsonld - the JSON-LD to verify
    """

    # frame data and retrieve signature
    frame = {
        '@context': payswarm.constants.CONTEXT_URL,
        'signature': {
            'type': {},
            'created': {},
            'creator': {},
            'signatureValue': {},
            # FIXME: improve handling signatures w/o nonces
            #'nonce': {'@omitDefault': True}
        }
    }
    framed = payswarm.jsonld.frame(jsonld, frame)
    graphs = framed['@graph']
    if len(graphs) == 0:
        raise Exception('No signed data found.')
    if len(graphs) > 1:
        raise Exception('More than one signed graph found.')
    graph = graphs[0]
    signature = graph['signature']
    if not signature:
        raise Exception('Valid signature not found.')
    if signature['type'] != 'GraphSignature2012':
        raise Exception('Unknown signature type found.')

    # check nonce
    if 'nonce' in signature:
        # FIXME add nonce checking
        #if not payswarm.hooks.check_nonce(signature['nonce']):
        #    raise Exception('The message nonce is invalid.')
        raise Exception('signature nonces not supported')

    # check date
    # enxure signature created within a valid range (+/- M minutes)
    now = datetime.datetime.utcnow()
    # FIXME: 15 minute default range, make this configurable
    delta = datetime.timedelta(minutes=15)
    # FIXME PyLD should do this automatically
    created = datetime.datetime.strptime(signature['created'], W3C_DATE_FORMAT)
    if created < (now - delta) or created > (now + delta):
        raise Exception(
            'The message digital signature timestamp is out of range.')

    # get public key
    if have_urllib3:
        _creator_res = urllib3pool.request('GET', signature['creator'])
        if _creator_res.status < 200 or _creator_res.status >= 300:
            raise Exception('Bad status code %d getting public key "%s"' %
                    ( r.status, signature['creator']))
        _creator_public_key_str = _creator_res.data
    else:
        _creator_stream = urllib2.urlopen(signature['creator'])
        _creator_public_key_str = _creator_stream.read()

    creator_public_key = json.loads(_creator_public_key_str)
    # FIXME frame key

    # verify publick key owner
    # FIXME
    #if not paysarm.hooks.is_trusted_authority(key.owner)
    #    raise Exception('The message is not signed by a trusted public key.')

    # ensure key has not been revoked
    if 'revoked' in creator_public_key:
        raise Exception('The public key has been revoked.')

    # normalize the data to be signed
    # remove signature property from object
    del framed['@graph'][0]['signature']
    # normalize
    normalized = payswarm.jsonld.normalize(framed, {
        'format': 'application/nquads'
    })

    # load the key
    public_key = RSA.importKey(creator_public_key['publicKeyPem'])

    # build the hash
    h = SHA256.new()
    if 'nonce' in signature:
        h.update(signature['nonce'])
    h.update(signature['created'])
    h.update(normalized)

    # verify signature
    signer = PKCS1_v1_5.new(public_key)
    if not signer.verify(h, signature['signatureValue'].decode('base64')):
        raise Exception('The digital signature on the message is invalid.')

    return True
