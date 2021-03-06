"""The payswarm module is used to perform a number of client operations 
such as registering with a PaySwarm Authority, generating public/private 
keys, digitally signing and registering assets for sale, registering listings, 
establishing Payment Sessions and performing purchases."""

import json
import os
import time
import urlparse

from Crypto.PublicKey import RSA
import pyld.jsonld as jsonld

import config
import constants
import purchase
import signature
import storage
import util

__all__ = ['config', 'jsonld', 'purchase', 'signature', 'storage', 'util']

class ConfigException(Exception):
    """The class of exceptions used for configuration errors."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PaySwarmClient(object):
    """The PaySwarm Client is used to communicate with the PaySwarm network."""

    def __init__(self):
        """Creates a new PaySwarm client using a provided configuration.

        config - The name of a config to load from disk or an dict that 
            contains configuration information. If one isn't given, the
            default will be used. If the value is a string,
            it should be a name of a config file stores in the PaySwarm
            config directory, or a filesystem pathname. If the value is a
            dict, the following keys are used by the client:
            
            {
              publicKey: { // the public key information object
                id: // the URL identifier for the public key
                publicKeyPem: // the public key in PEM format
                privateKeyPem: // the private key in PEM format
              }
              source: // the source account that funds should be taken from
              owner: // the owner of the config, keys, and account
            }
        """
        self.config = {}
        self.config['@context'] = constants.CONTEXT_URL

    def _get_config_filename(self, config_name):
        base = os.path.expanduser('~')
        if 'XDG_CONFIG_HOME' in os.environ:
            base = os.path.abspath(os.environ['XDG_CONFIG_HOME'])
            
        config_filename = os.path.join(base, '.config', 'payswarm1', 'default')
        
        # if a config name was not given, use the default    
        if config_name == None:
            return config_filename
        
        if os.path.isfile(config_name):
            # if a valid relative file name was given, use that
            config_filename = os.path.abspath(config_name)
        else:
            # if a configName was given, append it to the base config directory
            config_filename = \
                os.path.join(base,  '.config', 'payswarm1', config_name)
                
        return config_filename

    def create_key_pair(self):
        """Generates a public/private keypair for the client."""
        
        # generate the public/private keypair
        key_pair = RSA.generate(2048)

        # export public and private key to PEM format
        private_pem = key_pair.exportKey()
        public_pem = key_pair.publickey().exportKey()

        self.config['publicKey'] = {}
        self.config['publicKey']['privateKeyPem'] = private_pem
        self.config['publicKey']['publicKeyPem'] = public_pem

    def has_keys(self):
        """Returns whether or not the client has a valid set of keys."""
        
        keys_exist = 'publicKey' in self.config and \
          'publicKeyPem' in self.config['publicKey'] and \
          'privateKeyPem' in self.config['publicKey']
        
        return  keys_exist

    def decrypt(self, encrypted_message):
        """Generates a public/private keypair for the client."""
        
        message = {}
        
        message['destination'] = 'NOT IMPLEMENTED'
        message['owner'] = 'NOT IMPLEMENTED'
        message['publicKey'] = 'NOT IMPLEMENTED'
        
        # FIXME: Implement this function
        return message

    def get_config(self):
        """Return the current configuration for the PaySwarm client."""
        return self.config

    def load_config(self, config=None):
        """Loads a PaySwarm configuration into the client.
        
        config - The name of a config to load from disk or an dict that 
            contains configuration information. If one isn't given, the
            default will be used. If the value is a string,
            it should be a name of a config file stores in the PaySwarm
            config directory, or a filesystem pathname. If the value is a
            dict, the following keys are used by the client:
            
            {
              publicKey: { # the public key information object
                id: # the URL identifier for the public key
                publicKeyPem: # the public key in PEM format
                privateKeyPem: # the private key in PEM format
              }
              source: # the source account that funds should be taken from
              owner: # the owner of the config, keys, and account
            }
        """
        if isinstance(config, dict):
            self.config = config
        elif config == None or isinstance(config, basestring):
            config_filename = self._get_config_filename(config)
            
            if os.path.isfile(config_filename):
                config_file = open(config_filename, 'r')
                self.config = json.loads(config_file.read())
            else:
                raise ConfigException( \
                    'Config file does not exist: ' + config_filename)
        else:
            raise ConfigException( \
                'PaySwarmClient config must be either a string or dict.')

    def write_config(self, config=None):
        """Writes a PaySwarm configuration to the filesystem.
        
        config - A string that should either be a name of a config file 
            stored in the PaySwarm config directory, or a filesystem pathname.
        """
        config_filename = self._get_config_filename(config)
        config_dir = os.path.dirname(config_filename)

        # create the config directory if it doesn't already exist
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir, 0700)
            
        cfile = open(config_filename, 'w')
        configJson = json.dumps( \
            self.config, sort_keys=True, indent=2, separators=(',', ': '))
        cfile.write(configJson)

    def load_web_keys_config(self, authority):
        """Loads the Web Keys configuration from a given PaySwarm Authority.
        
        authority - the PaySwarm Authority URL to use when discovering the 
            Web Keys config.
        """
        
        # FIXME: Implement this function
        pass
    
    def get_registration_url(self):
        """Returns the Web Keys registration URL."""

        # FIXME: Implement this function
        return "https://example.com/register"

    def hash(self, message):
        """Returns a hash of a PaySwarm JSON-LD message."""

        # FIXME: Implement this function
        return 'notimplemented'
    
    def sign(self, message):
        """Returns a digitally signed JSON-LD object."""

        # FIXME: Implement this function
        return {'signature': 'NOT IMPLEMENTED'}

def w3c_date(i):
    """Return a valid W3C datetime given milliseconds since the epoch """
    # This function from: https://gist.github.com/mnot/246088
    year, month, day, hour, minute, second, wday, jday, dst = \
        time.gmtime(i)
    o = str(year)
    if (month, day, hour, minute, second) == (1, 1, 0, 0, 0): return o
    o = o + '-%2.2d' % month
    if (day, hour, minute, second) == (1, 0, 0, 0): return o
    o = o + '-%2.2d' % day
    if (hour, minute, second) == (0, 0, 0): return o
    o = o + 'T%2.2d:%2.2d' % (hour, minute)
    if second != 0:
        o = o + ':%2.2d' % second
    o = o + 'Z'
    
    return o

class Plugin(object):
    def get_name(self):
        raise NotImplementedError(self.get_name)

    def before_args_parsed(self, parser, subparsers):
        pass

    def after_args_parsed(self, args):
        pass
