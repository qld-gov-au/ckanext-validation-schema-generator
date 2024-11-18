# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from . import helpers
from .logic import action, auth, validators

from .flask_plugin import MixinPlugin


log = logging.getLogger(__name__)


class ValidationSchemaGeneratorPlugin(MixinPlugin, p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, './templates')
        tk.add_resource('./assets', 'validation_schema_generator')

    # IActions

    def get_actions(self):
        return action._get_actions()

    # IAuthFunctions

    def get_auth_functions(self):
        return auth._get_auth_functions()

    # ITemplateHelpers

    def get_helpers(self):
        return helpers._get_helpers()

    # IValidators

    def get_validators(self):
        return validators._get_validators()
