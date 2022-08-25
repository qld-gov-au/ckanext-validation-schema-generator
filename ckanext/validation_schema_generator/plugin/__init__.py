# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.exceptions import CkanVersionException

try:
    tk.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.validation_schema_generator.plugin.pylons_plugin import VSGMixinPlugin
else:
    from ckanext.validation_schema_generator.plugin.flask_plugin import VSGMixinPlugin


log = logging.getLogger(__name__)


class ValidationSchemaGeneratorPlugin(VSGMixinPlugin, p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, '../templates')
        tk.add_resource('../assets', 'validation_schema_generator')
