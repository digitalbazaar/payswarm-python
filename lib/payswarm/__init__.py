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
        ct = response.get("content-type", None)
        if ct == "application/json":
            return json.loads(content)
        elif ct == "application/x-www-form-urlencoded":
            return dict(urlparse.parse_qsl(content))
        else:
            # fallback to plain content
            return content

    def generate_registration_url(self):
        request_url = self.config.get("general", "oauth-request-url")
        authorize_url = self.config.get("general", "oauth-authorize-url")
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
        self.config.set("general", "oauth-registration-token", self.token.key)

        # Build the registration URL
        rval = authorize_url + "?oauth_token=%s" % self.token.key

        return rval

    def complete_registration(self, verifier):
        tokens_url = self.config.get("general", "oauth-tokens-url")
        self.token.set_verifier(verifier)

        response, content = self.request(tokens_url, "POST")
        self._check_response(response, content, 
            "Error: Failed to request a permanent registration token.")
        self.token = oauth.Token.from_string(content)

        # Write the registration token to the configuration
        self.config.set( \
            "general", "oauth-registration-secret", self.token.secret)










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

    def authorize_token(self):
        logging.debug("Authorize token")
        u = self.authority.authorize_url + "?oauth_token=" + self.token.key
        print "Visit this URL to authorize:"
        print u
        pin = ""
        while len(pin) == 0:
            pin = raw_input("What is the PIN? ")
        #resp, content = self.request(u, "POST")
        #self._check_response(resp, content, "Token authorization failure.")

        #print "\n*** Authorized ***"
        #print dict(urlparse.parse_qsl(content))

        #self.token.set_verifier(urlparse.parse_qs(content)["oauth_verifier"])
        self.token.set_verifier(pin)

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

