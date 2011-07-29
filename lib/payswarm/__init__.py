"""The payswarm module is used to perform a number of client operations 
such as registering with a PaySwarm Authority, generating public/private 
keys, digitally signing and registering assets for sale, registering listings, 
establishing Payment Sessions and performing purchases."""
import config
import json
import pyld.jsonld as jsonld
import oauth2 as oauth
import os
import purchase
import signature
import storage
import urlparse

__all__ = ["config", "jsonld", "purchase", "signature", "storage"]

class PaySwarmClient(oauth.Client):
    """The PaySwarm Client is used to communicate with any PaySwarm system."""

    def __init__(self, config, client_id, secret):
        """Creates a new PaySwarm client using a provided configuration.

        config - The configuration information for the PaySwarm client.
        client_id - the OAuth Client ID for the consumer.
        secret - the OAuth secret for the consumer.
        """
        oauth.Client.__init__(self, oauth.Consumer(client_id, secret))
        self.config = config

    def _check_response(self, response, content, error_message):
        """Checks the response from an based PaySwarm call.

        response - The HTTP response object.
        content - the body of the HTTP response.
        error_message - the error message to throw if there is an error.
        """
        code = int(response["status"])
        # check code is in 2xx range
        # HTTP request should have resolved 3xx issues
        if code < 200 or code >= 300:
            if response["content-type"] == "application/json":
                try:
                    content = json.loads(content)
                except UnicodeDecodeError, e:
                    print "UnicodeDecodeError(content) ==", content
                    raise Exception(error_message, code, content)
                #print json.dumps(content, indent=3)
            raise Exception(error_message, code, content)

    def _decode_response(self, response, content):
        """Checks the response from an based PaySwarm call.

        response - The HTTP response object.
        content - the body of the HTTP response, which will be decoded depending
            on the Content-Type.
        """
        ct = response.get("content-type", None)
        if ct == "application/json":
            return json.loads(content)
        elif ct == "application/x-www-form-urlencoded":
            return dict(urlparse.parse_qsl(content))
        else:
            # fallback to plain content
            return content

    def generate_registration_url(self):
        """Requests a registration token and returns a verification URL.

        Performs the first part of what is called an Out-Of-Band OAuth 
        verification. This type of verification is needed when operating 
        outside of a Web User Agent environment. 

        OAuth relies heavily on re-directs, if a re-direct mechanism isn't 
        available, all that can be done is to ask the person using the 
        application to go to a particular URL.

        Throws an exception if anything nasty happens.
        """
        request_url = self.config.get("general", "request-url")
        authorize_url = self.config.get("general", "authorize-url")
        params = {
            "oauth_callback": "oob",
            "scope": "payswarm-registration",
        }

        # Request a new registration token
        response, content = self.request(request_url, "POST", parameters=params)
        self._check_response(response, content, 
            "Error: Failed to request a temporary registration token.")

        # Extract the registration token information
        self.token = oauth.Token.from_string(content)

        # Write the registration token to the configuration
        self.config.set("application", "registration-token", self.token.key)

        # Build the registration URL
        rval = authorize_url + "?oauth_token=%s" % self.token.key

        return rval

    def generate_payment_session_url(self):
        """Requests a payment token and returns a verification URL.

        Performs the first part of what is called an Out-Of-Band OAuth 
        verification. This type of verification is needed when operating 
        outside of a Web User Agent environment. 

        OAuth relies heavily on re-directs, if a re-direct mechanism isn't 
        available, all that can be done is to ask the person using the 
        application to go to a particular URL.

        Throws an exception if anything nasty happens.
        """
        request_url = self.config.get("general", "request-url")
        authorize_url = self.config.get("general", "authorize-url")
        params = {
            "oauth_callback": "oob",
            "currency": "USD",
            "balance": "10.00",
            "scope": "payswarm-payment",
        }

        # Request a new registration token
        response, content = self.request(request_url, "POST", parameters=params)
        self._check_response(response, content, 
            "Error: Failed to request a temporary registration token.")

        # Extract the registration token information
        self.token = oauth.Token.from_string(content)

        # Write the registration token to the configuration
        self.config.set("client", "payment-token", self.token.key)

        # Build the registration URL
        rval = authorize_url + "?oauth_token=%s" % self.token.key

        return rval

    def complete_registration(self, verifier):
        """Completes the retrieval of a registration token.

        Performs the second part of what is called an Out-Of-Band OAuth 
        verification. This type of verification is needed when operating 
        outside of a Web User Agent environment. 

        OAuth relies heavily on re-directs, if a re-direct mechanism isn't 
        available, all that can be done is to ask the person using the 
        application to go to a particular URL. This step happens after the
        person has gone to the URL and verified the registration token
        request. They are given a verifier, which is given as input to this
        method.

        verifier - the verifier provided to the person after approving the
            registration token.

        Throws an exception if anything nasty happens.
        """
        tokens_url = self.config.get("general", "tokens-url")
        self.token.set_verifier(verifier)

        # get the registration token and secret
        response, content = self.request(tokens_url, "GET")
        self._check_response(response, content, 
            "Error: Failed to request a permanent registration token.")
        self.token = oauth.Token.from_string(content)

        # write the registration token to the configuration
        self.config.set( \
            "application", "registration-secret", self.token.secret)

    def authorize_payment_session(self, verifier):
        """Completes the retrieval of a payment token.

        Performs the second part of what is called an Out-Of-Band OAuth 
        verification. This type of verification is needed when operating 
        outside of a Web User Agent environment. 

        OAuth relies heavily on re-directs, if a re-direct mechanism isn't 
        available, all that can be done is to ask the person using the 
        application to go to a particular URL. This step happens after the
        person has gone to the URL and verified the payment session
        request. They are given a verifier, which is given as input to this
        method.

        verifier - the verifier provided to the person after approving the
            payment token.

        Throws an exception if anything nasty happens.
        """
        tokens_url = self.config.get("general", "tokens-url")
        self.token.set_verifier(verifier)

        # get the registration token and secret
        response, content = self.request(tokens_url, "GET")
        self._check_response(response, content, 
            "Error: Failed to request a payment token.")
        self.token = oauth.Token.from_string(content)

        # write the registration token to the configuration
        self.config.set( \
            "client", "payment-token", self.token.key)
        self.config.set( \
            "client", "payment-token-secret", self.token.secret)

    def call(self, url, error_message, post_data=None):
        """Performs a call against a URL using OAuth credentials.

        An OAuth Token must already be active for this client. The Token is
        used to authenticate and perform a call to the given URL. The standard
        HTTP method is GET unless post_data is supplied, then it's POST.

        Throws an exception if anything nasty happens.
        """
        response = None
        content = None

        # check to see if the call is a GET or a POST based on post_data
        if(post_data == None):
            response, content = self.request(url, "GET")
        else:
            response, content = self.request(url, "POST", parameters=post_data)

        self._check_response(response, content, error_message)
        return self._decode_response(response, content)

    def register_public_key(self):
        """Registers the public key stored in the config object.

        Registers the public key stored in the configuration file at the
        PaySwarm Authority and stores the URL to the key in the configuration
        file as well.

        Throws an exception if anything nasty happens.
        """
        key_url = self.config.get("application", "keys-url")
        public_key = self.config.get("application", "public-key")

        # perform the registration
        post_data = {"public_key": public_key}
        info = self.call(key_url, "Failed to register public key", post_data)
        
        # store the key URL in the configuration
        public_key_url = info["@subject"]
        self.config.set("application", "public-key-url", public_key_url)

    def set_token(self, token, secret):
        """Sets the token information directly.
        
        token - the token string.
        secret - the secret associated with the token.
        """
        self.token = oauth.Token(token, secret)

    def clear_token(self):
        """Clears the OAuth token information."""
        self.token = None

    def purchase(self, listing_url, listing_hash):
        """Performs a purchase given a listing URL and a hash.
        
        listing_url - the listing to purchase.
        listing_hash - the listing hash to provide a means of ensuring that
            the listing URL provided is the one that is intended to be 
            purchased.
        """
        rval = None
        
        contracts_url = self.config.get("general", "contracts-url")
        post_data = \
            { "listing": listing_url, "listing_hash": listing_hash }
        rval = self.call(
            contracts_url, "Failed to purchase contract", post_data)

        return rval

