"""The PaySwarm configuration module is used to read/write configs."""
from ConfigParser import ConfigParser
from Crypto.PublicKey import RSA
import json
import os.path
import urllib2

def _update_config(defaults, config, options, section, name):
    """"
    Updates a configuration value in the live configuration.
    """
    # add the section if it doesn't already exist
    if(not config.has_section(section)):
        config.add_section(section)
    
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

    # Update the configuration with the command line options, if the
    # options are different from the default or if the config doesn't
    # contain the options
    _update_config(defaults, config, options, "general", "authority")

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

def set_oauth(config, token, secret):
    """Stores the OAuth token and secret in the configuration file.
    
    config - the config to write the new keypair to. The public key is stored
        in the [general] section under 'public-key'. The private key is
        stored in the [general] section under 'private-key'."""

    config.set("general", "oauth-token", token)
    config.set("general", "oauth-secret", secret)

def retrieve_endpoints(config):
    """Retrieves the PaySwarm Authority Web Service endpoints.

    config - the config to retrieve the 'authority' configuration value
        from. The resulting web service endpoint URLs are written to the
        config under the [general] section 'oauth-authorize-url', 
        'oauth-request-url', and 'oauth-tokens-url'.

    Throws an exception if the retrieval was a failure."""

    # Create the client-config read request
    authority = config.get("general", "authority")
    print "AUTHORITY:", authority
    req = urllib2.Request(authority,
        headers = { "Content-Type": "application/json" })

    # Read the basic client configuration parameters from the URL
    f = urllib2.urlopen(req)
    aconfig = json.loads(f.read())

    # Extract the information from the authority configuration
    for k, v in aconfig:
        print k, v

def generate_keys(config):
    """Generates a new PKI keypair and stores it in the given config.
    
    config - the config to write the new keypair to. The public key is stored
        in the [general] section under 'public-key'. The private key is
        stored in the [general] section under 'private-key'."""

    private_key = RSA.generate(1024)
    public_key  = private_key.publickey()
    private_pem = private_key.exportKey()
    
    config.set("general", "private-key", private_pem)
    config.set("general", "public-key", public_key.exportKey())

