from __future__ import with_statement

import os
import logging
from ConfigParser import ConfigParser

from payswarm import Plugin


class Config(Plugin):
    def __init__(self):
        self.default_config_dir = \
                os.path.join(os.path.expanduser('~'), '.config', 'payswarm1')
        self.config_dir = \
                os.environ.get('PAYSWARM_CONFIG_DIR', self.default_config_dir)

        self.main_config = ConfigParser()
        self.profile_config = ConfigParser()

        self.main_config_path = os.path.join(self.config_dir, 'payswarm1.cfg')
        self.main_config.read([self.main_config_path])

    def get_name(self):
        return "FilesConfig"

    def before_args_parsed(self, parser, subparsers):
        profile = self.value('application', 'profile')
        parser.add_argument('-p', '--profile', default=profile,
                help='Select the configuration profile to use. (default: %(default)s)')
        parser.add_argument('--set-profile', action='store_true',
                help='Set the profile in the main config file. (default: %(default)s)')

        subparser = subparsers.add_parser('config')
        # FIXME: this should change to the root authority URL once services
        # discovery method is developed
        subparser.add_argument('-u', '--url',
                help='The PaySwarm Authority client configuration URL.')
        subparser.set_defaults(func=self.run)

    def after_args_parsed(self, args):
        if args.profile is not None:
            profile = args.profile
            self.set('application', 'profile', args.profile, main=True)
        else:
            profile = self.value('application', 'profile')
        if args.set_profile:
            self.save(main=True)
        self.profile_config_path = os.path.join(
                self.config_dir, 'profiles', profile, 'payswarm1.cfg')
        self.profile_config.read([self.profile_config_path])

    def values(self, subject, property):
        # only support single values of ConfigParser
        if self.profile_config.has_option(subject, property):
            yield self.profile_config.get(subject, property)
        elif self.main_config.has_option(subject, property):
            yield self.main_config.get(subject, property)

    def value(self, subject, property):
        values = list(self.values(subject, property))
        if len(values) > 1:
            raise Exception('too many values for %s::%s' % (subject, property))
        return values[0]

    def properties(self, subject):
        # return profile properties
        if self.profile_config.has_section(subject):
            for p in self.profile_config.options(subject):
                yield p
        # then return main properties if not in profile
        if self.main_config.has_section(subject):
            for p in self.main_config.options(subject):
                if not self.profile_config.has_option(subject, p):
                    yield p

    def set(self, subject, property, value, main=False):
        c = self.main_config if main else self.profile_config
        c.set(subject, property, value)

    def save(self, main=False):
        c = self.main_config if main else self.profile_config
        path = self.main_config_path if main else self.profile_config_path

        with open(path, 'w') as f:
            c.write(f)

    def run(self, args):
        print 'config', args
