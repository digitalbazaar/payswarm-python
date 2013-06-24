"""The PaySwarm configuration module is used to read/write configs."""
from __future__ import with_statement

import json
import logging
import os

from .util import Plugin
from pyld.jsonld import JsonLdProcessor as JsonLdProcessor

"""
Config directory is:
    PAYSWARM_CONFIG_DIR else
    ~/.config/payswarm1

Main config is loaded from:
    PAYSWARM_MAIN_CONFIG_PATH else
    PAYSWARM_CONFIG_DIR/payswarm.json

Session config is loaded from:
    value passed to -c/--config else
    PAYSWARM_CONFIG_PATH else
    PAYSWARM_CONFIG_DIR/configs/default.json

When loading session config, try:
    If name doesn't look like a path, load:
        PAYSWARM_CONFIG_DIR/configs/{CONFIG_NAME}.json
    else:
        load as a path

Main config format:
    {
        "defaultConfig": "{PATH} or {CONFIG_NAME}",
        "python": {
            "pluginPath": ["path1", ...],
            "plugins": ["plugin1", ...]
        }
        ...
    }

Session config format:
    {
        "@context": "https://w3id.org/payswarm/v1",
        "authority": "https://{URL}/",
        "owner": "https://{URL}/i/{ID}",
        "publicKey": {
            "publicKeyPem": "...",
            "privateKeyPem": "...",
            "id": "https://{URL}/i/{ID}/keys/{KEY}"
        },
        "source": "https://{URL}/i/{ID}/accounts/{ACCOUNT}"
    }
"""


class Config(dict):

    def has_property(self, property):
        return JsonLdProcessor.has_property(self, property)

    def has_value(self, property, value):
        return JsonLdProcessor.has_value(self, property, value)

    def get_values(self, property):
        return JsonLdProcessor.get_values(self, property)

    def get_value(self, property):
        values = list(self.get_values(property))
        if len(values) > 1:
            raise Exception('too many values for "%s"' % (property))
        return values[0]

    def load(self, path, clear=True):
        if clear:
            self.clear()
        with open(path) as config:
            self.update(json.load(config))

    def save(self, path):
        with open(path, 'w') as config:
            config.write(json.dumps(self))


class Files(Plugin):
    """Plugin to load PaySwarm configuration from files."""

    def __init__(self):
        # top level config dir
        self.default_config_dir = \
                os.path.join(os.path.expanduser('~'), '.config', 'payswarm1')
        self.config_dir = \
                os.environ.get('PAYSWARM_CONFIG_DIR', self.default_config_dir)

        # main config file path
        self.default_main_config_path = \
                os.path.join(self.config_dir, 'payswarm.json')
        self.main_config_path = \
                os.environ.get('PAYSWARM_MAIN_CONFIG_PATH',
                        self.default_main_config_path)

        # load main config
        self.main_config = Config()
        self.main_config.load(self.main_config_path)

        # session config file path
        self.default_config_path = \
                os.path.join(self.config_dir, 'configs', 'default.json')
        self.config_path = \
                self.main_config.get('defaultConfig', '') or \
                os.environ.get('PAYSWARM_CONFIG_PATH',
                        self.default_config_path)

        # load config after args processed
        self.config = Config()

    def get_name(self):
        return "FilesConfig"

    def before_args_parsed(self, parser, subparsers):
        default = self.main_config.get('defaultConfig', self.config_path)
        parser.add_argument('-c', '--config', default=self.config_path,
                help='Select the configuration to use. (default: %(default)s)')
        parser.add_argument('--set-config', action='store_true',
                help='Set the default config in the main config file. (default: %(default)s)')

        subparser = subparsers.add_parser('config')
        # FIXME: this should change to the root authority URL once services
        # discovery method is developed
        subparser.add_argument('-u', '--url',
                help='The PaySwarm Authority client configuration URL.')
        subparser.set_defaults(func=self.run)

    def after_args_parsed(self, args):
        self.config.load(self.config_path)

        if args.config is not None:
            self.config_path = args.config
        # FIXME check if path exists else try .../configs/{config}.json
        if args.set_config:
            self.main_config['defaultConfig'] = self.config_path
            self.main_config.save(self.main_config_path)

    def run(self, args):
        pass


from Crypto.PublicKey import RSA
import json
import os.path
import urllib2



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
    uconfig = os.path.join(
            os.path.expanduser("~"),
            ".config", "payswarm1", "profiles", options.profile, "payswarm1.cfg")
    sysconfig = os.path.join("/", "etc", "payswarm1", "payswarm1.cfg")
    cfiles = [sysconfig, uconfig]
    if options.config:
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
    _update_config(defaults, config, options, "general", "authority-url")
    _update_config(defaults, config, options, "general", "config-url")
    _update_config(defaults, config, options, "general", "listings-url")

    # If the user's configuration file doesn't exist, create it
    if(not os.path.exists(uconfig)):
        save(config, options)

    return config

def save(config, options):
    """Saves the given configuration file to the user's payswarm config.
    
    config - the configuration object to save.
    options - the app options.
    """
    uconfig = os.path.join(
            os.path.expanduser("~"),
            ".config", "payswarm1", "profiles", options.profile, "payswarm1.cfg")

    dir = os.path.dirname(uconfig)
    if not os.path.exists(dir):
        os.makedirs(dir)
    ufile = open(uconfig, "w")
    config.write(ufile)
    ufile.close()

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
                account_id = account["id"]
                config.set( \
                    "application", "financial-account", account_id)
        elif(key == PSP_LICENSE):
            licenses = value
            for license in licenses:
                license_id = license["id"]
                license_hash = license[PS_LICENSE_HASH]
                config.set("application", "default-license", license_id)
                config.set("application", "default-license-hash", license_hash)

def generate_keys(config):
    """Generates a new PKI keypair and stores it in the given config.
    
    config - the config to write the new keypair to. The public key is stored
        in the [general] section under 'public-key'. The private key is
        stored in the [general] section under 'private-key'."""
    # generate the public/private keypair
    key_pair = RSA.generate(2048)
    
    # export public and private key to PEM format
    private_pem = key_pair.exportKey()
    public_pem = key_pair.publickey().exportKey()
    
    # save the key data into the configuration file
    config.set("application", "private-key", private_pem)
    config.set("application", "public-key", public_pem)
