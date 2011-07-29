"""The PaySwarm configuration module is used to read/write configs."""
from ConfigParser import ConfigParser
import M2Crypto
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

    # create each application section if it doesn't already exist in the config
    for section in ["general", "application", "client"]:
        if(not config.has_section(section)):
            config.add_section(section)

    # Update the configuration with the command line options, if the
    # options are different from the default or if the config doesn't
    # contain the options
    _update_config(defaults, config, options, "general", "config-url")
    _update_config(defaults, config, options, "general", "listings-url")

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
    for key, value in aconfig.items():
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
    for key, value in endpoints.items():
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
    for key, value in preferences.items():
        if(key == PS_ACCOUNT):
            accounts = value
            for account in accounts:
                account_id = account["@subject"]
                config.set( \
                    "application", "financial-account", account_id)
        elif(key == PSP_LICENSE):
            licenses = value
            for license in licenses:
                license_id = license["@subject"]
                license_hash = \
                    license[PS_LICENSE_HASH]
                config.set("application", "default-license", license_id)
                config.set("application", "default-license-hash", license_hash)

def generate_keys(config):
    """Generates a new PKI keypair and stores it in the given config.
    
    config - the config to write the new keypair to. The public key is stored
        in the [general] section under 'public-key'. The private key is
        stored in the [general] section under 'private-key'."""
    # create buffers to hold the key data
    private_bio = M2Crypto.BIO.MemoryBuffer()
    public_bio = M2Crypto.BIO.MemoryBuffer()
    
    # generate the public/private keypair
    key_pair = M2Crypto.RSA.gen_key(1024, 65537)
    
    # export public and private key to PEM format
    key_pair.save_key_bio(private_bio, cipher=None)
    key_pair.save_pub_key_bio(public_bio)
    private_pem = private_bio.read().strip()
    public_pem = public_bio.read().strip()
    
    # save the key data into the configuration file
    config.set("application", "private-key", private_pem)
    config.set("application", "public-key", public_pem)

