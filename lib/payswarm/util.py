"""PaySwarm utilities."""

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

import hashlib

import payswarm

def hash(obj):
    """
    Generates a hash of the JSON-LD encoded data.

    @param obj the JSON-LD object to hash.
    @param callback(err, hash) called once the operation completes.
    """
    normalized = payswarm.jsonld.normalize(obj, {
        'format': 'application/nquads'
    })

    if len(normalized) == 0:
        raise Exception('Attempt to hash empty normalized data.')

    return 'urn:sha256:' + hashlib.sha256(normalized).hexdigest()


def inline_context(jsonld):
    """
    Inline full version of known PaySwarm contexts.
    """
    def _inline(ctx):
        if ctx in payswarm.constants.CONTEXTS:
            return payswarm.constants.CONTEXTS[ctx]
        return ctx
    if '@context' in jsonld:
        if isinstance(jsonld['@context'], str):
            jsonld['@context'] = _inline(jsonld['@context'])
        elif isinstance(jsonld['@context'], list):
            jsonld['@context'] = [_inline(el) for el in jsonld['@context']]
