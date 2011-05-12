"""The payswarm module is used to perform a number of client operations 
such as registering with a PaySwarm Authority, generating public/private 
keys, digitally signing and registering assets for sale, registering listings, 
establishing Payment Sessions and performing purchases."""
import json
import oauth2 as oauth
import os
import urlparse
import config

__all__ = ['config']

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
        public_key_url = info["@"].lstrip("<").rstrip(">")
        self.config.set("application", "public-key-url", public_key_url)

    def get_request_token(self):
        logging.debug("Get request token")
        params = {
            "oauth_callback": CALLBACK_URL,
            "currency": "USD",
            "balance": "2.00",
            "scope": "payswarm-payment",
        }
        resp, content = self.request(self.authority.request_url, "POST",
                parameters=params)
        self._check_response(resp, content, "Token request failure.")

        #print "\n*** Request ***"
        #logging.debug("resp")
        self.token = oauth.Token.from_string(content)
        #print dict(urlparse.parse_qsl(self.token))
        return self.token

    def get_payment_token(self):
        resp, content = self.request(self.authority.access_url, "POST")
        self._check_response(resp, content, "Payment token request failure.")
        self.token = oauth.Token.from_string(content)
        print "PAYMENT TOKEN", self.token.key, self.token.secret
        return self.token

    def _contracts_request(self, listing_url, listing_hash, verify=False):
        method = "GET"
        params = {}
        if verify:
            # FIXME: Implement asset verification
            print "_contracts_request(): VERIFY NOT IMPLEMENTED!"
        else:
            method = "POST"
            params["listing"] = listing_url
            params["listing_hash"] = listing_hash
        resp, content = self.request(
            self.authority.contracts_url, method, parameters=params)
        msg = "Verify failure." if verify else "Purchase failure."
        self._check_response(resp, content, msg)
        return self._decode_response(resp, content)

    def purchase(self, listing_url, listing_hash, verify_only=False):
        return self._contracts_request(listing_url, listing_hash, verify=False)

    def verify(self):
        return self._contracts_request(verify=True)

