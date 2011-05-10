"""The payswarm module is used to perform a number of client operations 
such as registering with a PaySwarm Authority, generating public/private 
keys, digitally signing and registering assets for sale, registering listings, 
establishing Payment Sessions and performing purchases."""
import json
import oauth2 as oauth
import os
import urlparse
import config

class PaySwarmAuthority(object):
    def __init__( \
        self, authority_url="https://dev.payswarm.com/", discover_api=False):
        self._authority_url = authority_url
        if discover_api:
            self.discover_api()
        else:
            self._update_api()

    def _update_api(self):
        """Update authority URL fields."""
        api = self._authority_url
        oauth_api = os.path.join(api, "oauth1/")
        self.request_url = os.path.join(oauth_api, "tokens/request")
        self.authorize_url = os.path.join(api, "profile/tokens/authorize")
        self.access_url = os.path.join(oauth_api, "tokens")
        self.contracts_url = os.path.join(api, "contracts")
        self.asset_info_url = os.path.join(api, "assets")
        self.license_info_url = os.path.join(api, "license")
        self.listing_info_url = os.path.join(api, "listings")

    def discover_api(self):
        """Use service discovery to find PaySwarm API URLs."""
        # FIXME Use service discovery to find api path
        self._api_path = ""
        self._update_api()

class PaySwarmClient(oauth.Client):
    """PaySwarm OAuth Client"""

    def __init__(self, authority, token=None, secret=None, **args):
        if authority is not None and \
            not isinstance(authority, PaySwarmAuthority):
            raise ValueError("Invalid authority.")
        self.authority = authority

        # Create the OAuth client
        # FIXME: set the proper client ID and client secret
        consumer = oauth.Consumer(token, secret)
        if(token):
            self.token = oauth.Token(token, secret)
            oauth.Client.__init__(self, consumer, self.token, **args)
        else:
            oauth.Client.__init__(self, consumer, **args)

    def _check_response(self, response, content, error_message):
        code = int(response["status"])
        # check code is in 2xx range
        # http request should have resolved 3xx issues
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

