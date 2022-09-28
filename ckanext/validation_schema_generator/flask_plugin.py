# -*- coding: utf-8 -*-

import ckan.plugins as p

from .views import vsg


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [vsg]
