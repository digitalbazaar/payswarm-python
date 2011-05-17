"""The JSON-LD module is used for performing normalization of JSON-LD."""
import copy
import json

# FIXME: This code will be replaced very soon with proper JSON-LD 
# normalization code from the new specification.

# The default context is defined by the JSON-LD specification
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_ANYURI = "http://www.w3.org/2001/XMLSchema#anyURI"
XSD_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
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
            "http://www.w3.org/2001/XMLSchema#dateTime" \
    } \
}

# FIXME: This default context is used when uploading to overcome a limitation
# of the reference PaySwarm Authority implementation.
FAKE_DEFAULT_CONTEXT = { \
         "#types": { \
            "com:date": "xsd:dateTime", \
            "com:destination": "xsd:anyURI", \
            "com:payeePosition": "xsd:integer", \
            "dc:created": "xsd:dateTime", \
            "dc:creator": "xsd:anyURI", \
            "ps:asset": "xsd:anyURI", \
            "ps:assetProvider": "xsd:anyURI", \
            "ps:authority": "xsd:anyURI", \
            "ps:contentUrl": "xsd:anyURI", \
            "ps:license": "xsd:anyURI" \
         }, \
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
         "xsd": "http://www.w3.org/2001/XMLSchema#" \
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
    # Expand all of the properties first
    for key, value in data.items():
        # FIXME: add proper context handling
        # for now, always remove the context
        if(key == "#"):
            del data["#"]
        if(key == "a"):
            data["<" + RDF_TYPE + ">"] = value
            del data[key]
            key = "<" + RDF_TYPE + ">"
        elif(":" in key):
            iri = _expand_curie(key)
            data[iri] = value
            if(iri != key):
                del data[key]
                # Set the 'active' key to the newly expanded iri
                key = iri

    # Expand all of the objects second
    for key, value in data.items():
        # expand all of the object CURIEs next
        if(type(value) == type({})):
            # recursively expand the CURIEs for the value if it is an object
            _expand_curies(value)
        elif(type(value) == type([])):
            # expand all CURIEs contained in arrays
            newarr = []
            for item in value:
                # expand all string values of concern
                if(type(item) == type("") or type(item) == type(u"")):
                    if((RDF_TYPE in key) \
                        or (item.startswith("<") and item.endswith(">"))):
                            iri = _expand_curie(item)
                            newarr.append(iri)
                    else:
                        newarr.append(item)
                elif(type(item) == type({})):
                    # expand objects recursively and add them to the newarr
                    _expand_curies(item)
                    newarr.append(item)
            data[key] = newarr
        elif(type(value) == type("") or type(value) == type(u"")):
            # expand string values that are either types or CURIEs
            if((RDF_TYPE in key) or \
                (value.startswith("<") and value.endswith(">"))):
                data[key] = _expand_curie(value)

def _coerce_iri(value):
    """Coerces the given value to an IRI if it isn't already one.
    
    value - the string value to coerce.
    
    Returns a valid JSON-LD IRI.
    """
    rval = value
    
    # if the IRI is not enclosed in <>, enclose it
    if(not value.startswith("<") or not value.endswith(">")):
        rval = "<" + value + ">"
    
    return rval

def _coerce_typed_literal(value, datatype):
    """Coerces the given value to a given datatype.
    
    value - the string value to coerce.
    datatype - the datatype to coerce the value to.
    
    Returns a valid JSON-LD typed literal.
    """
    rval = str(value)
    dtstring = "^^<" + datatype + ">"

    # if the value doesn't end in the typed literal syntax, enclose it    
    if(not rval.endswith(dtstring)):
        rval = str(value) + dtstring

    return rval

def _coerce_types(data):
    """Coerces values in a JSON-LD structure into a normalized form.

    data - the given data object, which will have all of the objects
        coerced into the proper normalized form.
    """
    for key, value in data.items():
        coerce_iri = False
        coerce_type = None
        
        # if the key is @ or rdf:type, coerce the object to an IRI
        if((key == "@") or (RDF_TYPE in key)):
            coerce_iri = True
        else:
            # if key exists in type coercion list, coerce to datatype
            for prop, datatype in DEFAULT_CONTEXT["#types"].items():
                prop = "<" + prop + ">"
                if(prop == key):
                    if(datatype == XSD_ANYURI):
                        coerce_iri = True
                    else:
                        coerce_type = datatype
                elif(type(value) == type(0)):
                    coerce_type = XSD_INTEGER

        # perform the coercion
        if(coerce_iri):
            if(type(value) == type("") or type(value) == type(u"")):
                # if string, coerce to an IRI
                data[key] = _coerce_iri(value)
            elif(type(value) == type([])):
                # if array, coerce each item to an IRI
                newarr = []
                for item in value:
                    if(type(item) == type("") or type(item) == type(u"")):
                        newarr.append(_coerce_iri(item))
                data[key] = newarr
        elif(coerce_type != None):
            if(type(value) == type("") or type(value) == type(u"") or
               type(value) == type(0)):
                # if string, coerce to a typed literal
                data[key] = _coerce_typed_literal(value, coerce_type)
            elif(type(value) == type([])):
                # if array, coerce each item to a typed literal
                newarr = []
                for item in value:
                    if(type(value) == type("") or type(value) == type(u"")):
                        newarr.append(_coerce_typed_literal(item, coerce_type))
                data[key] = _coerce_array(value)
        elif(type(value) == type([])):
            newarr = []
            for item in value:
                if(type(item) == type({})):
                    # perform the coercion recursively on objecs
                    _coerce_types(item)
                    newarr.append(item)
                elif(type(item) == type("") or type(item) == type(u"")):
                    # copy string values directly
                    newarr.append(item)
            data[key] = newarr
        elif(type(value) == type({})):
            # coerce recursively on objects
            _coerce_types(value)

def _flatten(data):
    """Flattens all embedded subjects into a top-level subject.

    data - the given data object, which will have all of the objects
        coerced into the proper normalized form.
    """
    rval = {"@": []}
    flattened = copy.deepcopy(data)
    embeds = []
    
    # FIXME: This algorithm is crap as it only goes down one level, and
    # doesn't sort the contents of the arrays.
    for key, value in flattened.items():
        if(type(value) == type({})):
            if(value.has_key("@")):
                embeds.append(value)
                flattened[key] = value["@"]

    # if there are embeds, place them into the top-level array
    # FIXME: For some reason, this breaks how resources are stored on the
    # PaySwarm Authority
    if(len(embeds) > 0):
        for embed in embeds:
            rval["@"].append(embed)
        rval["@"].append(flattened)
    else:
        rval = flattened
    
    return rval

def normalize(arr):
    """Performs JSON-LD normalization of a given associative array.

    arr - the associative array to normalize based on the JSON-LD specification
        normalization rules.

    Returns the normalized JSON-LD string value of the given array.
    """
    rval = ""
    norm = copy.deepcopy(arr)

    # expand all CURIEs into their final IRI form
    _expand_curies(norm)
    #print "CURIES_EXPANDED:", json.dumps(norm, indent=3, sort_keys=True)
    # perform type coercion on the types that should be coerced
    _coerce_types(norm)
    #print "NORMALIZED:", json.dumps(norm, indent=3, sort_keys=True)
    # move all embedded objects into the top-level object
    norm = _flatten(norm)
    #print "FLATTENED:", json.dumps(norm, indent=3, sort_keys=True)
    
    # sort the keys and compress the JSON
    rval = json.dumps(norm, sort_keys=True, separators=(',', ':'))
    
    return rval

