"""The PaySwarm configuration module is used to read/write configs."""
from ConfigParser import ConfigParser
import os.path

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
        ufile = open(uconfig, "w")
        config.write(ufile)
        ufile.close()

    return config

