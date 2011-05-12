"""The PaySwarm configuration module is used to read/write configs."""
from ConfigParser import ConfigParser
from Crypto.PublicKey import RSA
import json
import os.path
import urllib2

# Constants used by the configuration service
PSW_REQUEST = "http://purl.org/payswarm/webservices#oAuthRequest"
PSW_AUTHORIZE = "http://purl.org/payswarm/webservices#oAuthAuthorize"
PSW_TOKENS = "http://purl.org/payswarm/webservices#oAuthTokens"
PSW_PREFERENCES = "http://purl.org/payswarm/webservices#oAuthPreferences"
PSW_CONTRACTS = "http://purl.org/payswarm/webservices#oAuthContracts"
PSW_LICENSES = "http://purl.org/payswarm/webservices#oAuthLicenses"
PSW_KEYS = "http://purl.org/payswarm/webservices#oAuthKeys"
# FIXME: This is an error below - should be payswarm#account
PS_ACCOUNT = "http://purl.org/payswarm/#account"
PS_LICENSE_HASH = "http://purl.org/payswarm#licenseHash"
PSP_LICENSE = "http://purl.org/payswarm/preferences#license" 

def _update_config(defaults, config, options, section, name):
    """"
    Updates a configuration value in the live configuration.
    """    
    if(not config.has_option(section, name)):
        # if the option doesn't exist in the config, set it
        config.set(section, name, getattr(options, name))
    else:
        # if the option does exist in the config, but a non-default one is
        # specified, use the new value
        is_default = (getattr(options, name) == defaults[name])
        if(not is_default):
            config.set(section, name, getattr(options, name))

def parse(defaults, options):
    """
    Parses the list of configuration files from the system.
    """
    uconfig = os.path.expanduser('~/.payswarm1')
    cfiles = ['/etc/payswarm1.cfg', uconfig]
    if(options.config != None):
        cfiles.append(options.config)
    config = ConfigParser()
    config.read(cfiles)

    # add the general section if it doesn't already exist
    if(not config.has_section("general")):
        config.add_section("general")

    # add the application section if it doesn't already exist
    if(not config.has_section("application")):
        config.add_section("application")

    # Update the configuration with the command line options, if the
    # options are different from the default or if the config doesn't
    # contain the options
    _update_config(defaults, config, options, "general", "config-url")

    # If the user's configuration file doesn't exist, create it
    if(not os.path.exists(uconfig)):
        save(config)

    return config

def save(config):
    """Saves the given configuration file to the user's payswarm config.
    
    config - the configuration object to save.
    """
    uconfig = os.path.expanduser('~/.payswarm1')

    ufile = open(uconfig, "w")
    config.write(ufile)
    ufile.close()

def set_oauth_credentials(config, client_id, secret):
    """Stores the OAuth token and secret in the configuration file.
    
    config - the config to write the OAuth credentials to. The client_id is 
        stored in the [application] section under 'client-id'. The private 
        key is stored in the [application] section under 'client-secret'."""

    config.set("application", "client-id", client_id)
    config.set("application", "client-secret", secret)

def set_basic_endpoints(config):
    """Retrieves the PaySwarm Authority Web Service endpoints.

    config - the config to retrieve the 'authority' configuration value
        from. The resulting web service endpoint URLs are written to the
        config under the [general] section 'authorize-url', 
        'request-url', and 'tokens-url'.

    Throws an exception if the retrieval was a failure."""

    # Create the client-config read request
    config_url = config.get("general", "config-url")

    # Read the basic client configuration parameters from the URL
    data = urllib2.urlopen(config_url)
    aconfig = json.loads(data.read())

    # Extract the information from the authority configuration
    for k, v in aconfig.items():
        key = k.lstrip("<").rstrip(">")
        value = v.lstrip("<").rstrip(">")
        if(key == PSW_REQUEST):
            config.set("general", "request-url", value)
        elif(key == PSW_AUTHORIZE):
            config.set("general", "authorize-url", value)
        elif(key == PSW_TOKENS):
            config.set("general", "tokens-url", value)

def set_application_endpoints(client, config):
    """Retrieves and sets all of the application endpoints.

    config - The following items will be updated in the
        configuration under the [general] section: authorize-url, 
        request-url, tokens-url, preferences-url, contracts-url,
        licenses-url, and keys-url.
    """
    # Retrieve the application endpoints
    authority_url = config.get("general", "config-url")
    endpoints = client.call( \
        authority_url, "Failed to retrieve application endpoints.")

    # Extract the information from the authority configuration
    for k, v in endpoints.items():
        key = k.lstrip("<").rstrip(">")
        value = v.lstrip("<").rstrip(">")
        if(key == PSW_REQUEST):
            config.set("general", "request-url", value)
        elif(key == PSW_AUTHORIZE):
            config.set("general", "authorize-url", value)
        elif(key == PSW_TOKENS):
            config.set("general", "tokens-url", value)
        elif(key == PSW_PREFERENCES):
            config.set("application", "preferences-url", value)
        elif(key == PSW_CONTRACTS):
            config.set("general", "contracts-url", value)
        elif(key == PSW_LICENSES):
            config.set("general", "licenses-url", value)
        elif(key == PSW_KEYS):
            config.set("application", "keys-url", value)
        else:
            print "UNKNOWN %s: %s" % (key, value)

def set_application_preferences(client, config):
    """Retrieves and sets all of the application preferences.

    config - The following items will be updated in the
        configuration under the [general] section: .
    """
    # Retrieve the application endpoints
    preferences_url = config.get("application", "preferences-url")
    preferences = client.call( \
        preferences_url, "Failed to retrieve application endpoints.")

    # Extract the information from the authority configuration
    for k, v in preferences.items():
        key = k.lstrip("<").rstrip(">")
        if(key == PS_ACCOUNT):
            accounts = v
            for account in accounts:
                account_id = account["@"].lstrip("<").rstrip(">")
                config.set( \
                    "application", "financial-account", account_id)
        elif(key == PSP_LICENSE):
            licenses = v
            for license in licenses:
                license_id = license["@"].lstrip("<").rstrip(">")
                license_hash = \
                    license["<" + PS_LICENSE_HASH + ">"].lstrip("<").rstrip(">")
                config.set("application", "default-license", license_id)
                config.set("application", "default-license-hash", license_hash)

def generate_keys(config):
    """Generates a new PKI keypair and stores it in the given config.
    
    config - the config to write the new keypair to. The public key is stored
        in the [general] section under 'public-key'. The private key is
        stored in the [general] section under 'private-key'."""

    private_key = RSA.generate(1024)
    public_key  = private_key.publickey()
    private_pem = private_key.exportKey()
    
    config.set("application", "private-key", private_pem)
    config.set("application", "public-key", public_key.exportKey())

