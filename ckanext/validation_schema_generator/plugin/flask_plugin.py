# -*- coding: utf-8 -*-

import ckan.plugins as p

from ckanext.validation_schema_generator.views import vsg

class VSGMixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [vsg]
