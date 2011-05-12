"""The JSON-LD module is used for performing normalization of JSON-LD."""
import json

def normalize(arr):
    """Performs JSON-LD normalization of a given associative array.

    arr - the associative array to normalize based on the JSON-LD specification
        normalization rules.

    Returns the normalized JSON-LD string value.
    """

    return json.dumps(arr)

