"""The JSON-LD module is used for performing normalization of JSON-LD."""
import copy
import json

# The default context is defined by the JSON-LD specification
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
DEFAULT_CONTEXT = \
{ \
    "com": "http://purl.org/commerce#", \
    "dc": "http://purl.org/dc/terms/", \
    "foaf": "http://xmlns.org/foaf/0.1/", \
    "gr": "http://purl.org/goodrelations/v1#", \
    "ps": "http://purl.org/payswarm#", \
    "psp": "http://purl.org/payswarm/preferences#", \
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", \
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#", \
    "sig": "http://purl.org/signature#", \
    "vcard": "http://www.w3.org/2006/vcard/ns#", \
    "xsd": "http://www.w3.org/2001/XMLSchema#", \
    "#types": \
    { \
        "http://purl.org/commerce#destination": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/commerce#payeePosition": \
            "http://www.w3.org/2001/XMLSchema#integer", \
        "http://purl.org/dc/terms/created": \
            "http://www.w3.org/2001/XMLSchema#dateTime", \
        "http://purl.org/dc/terms/creator": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/payswarm#asset": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/payswarm#assetProvider": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/payswarm#authority": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/payswarm#contentUrl": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/payswarm#license": \
            "http://www.w3.org/2001/XMLSchema#anyURI", \
        "http://purl.org/commerce#date": \
            "http://www.w3.org/2001/XMLSchema#dateTime"
    } \
}

def _expand_curie(curie):
    """Expands a single CURIE or returns the unexpanded value back.

    curie - the CURIE to expand.

    Return the expanded CURIE if it can be expanded, or the given value if it
    cannot be expanded.
    """
    rval = curie.lstrip("<").rstrip(">")

    if(":" in rval):
        # if there is a colon, split on it and attempt to expand the prefix
        prefix, reference = rval.split(":", 1)
        if(prefix in DEFAULT_CONTEXT.keys()):
            rval = "<" + DEFAULT_CONTEXT[prefix] + reference + ">"
    elif(rval in DEFAULT_CONTEXT.keys()):
        # if there is no colon, attempt to expand the entire CURIE as a term
        rval = "<" + DEFAULT_CONTEXT[rval] + ">"

    return rval

def _expand_curies(data):
    """Expands CURIEs contained in the data.

    data - the given data object, which will have all of its CURIEs expanded
        in-place.
    """
    for key, value in data.items():
        # expand the key CURIE first
        if(key == "a"):
            data["<" + RDF_TYPE + ">"] = value
            del data["a"]
        elif(":" in key):
            iri = _expand_curie(key)
            data[iri] = value
            if(iri != key):
                del data[key]
                # Set the 'active' key to the newly expanded iri
                key = iri

        # expand all of the object CURIEs next
        if(type(value) == type({})):
            # recursively expand the CURIEs for the value if it is an object
            _expand_curies(value)
        elif(type(value) == type([])):
            # expand all CURIEs contained in arrays
            newarr = []
            for item in value:
                # expand all string values of concern
                if(type(item) == type("")):
                    if(key == RDF_TYPE \
                        or (item.startswith("<") and item.endswith(">"))):
                            iri = _expand_curie(item)
                            newarr.append(iri)
                    else:
                        newarr.append(item)
                elif(type(item) == type({})):
                    _expand_curies(item)
            data[key] = newarr
        elif(type(value) == type("")):
            if(key == "<" + RDF_TYPE + ">"):
                data[key] = _expand_curie(value)

    #print "EXPANDED CURIES: ", json.dumps(data, sort_keys = True, indent = 3)

def normalize(arr):
    """Performs JSON-LD normalization of a given associative array.

    arr - the associative array to normalize based on the JSON-LD specification
        normalization rules.

    Returns the normalized JSON-LD string value of the given array.
    """
    norm = copy.deepcopy(arr)

    _expand_curies(norm)
    #_coerce_types(norm)

    return json.dumps(arr)

