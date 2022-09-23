# -*- coding: utf-8 -*-

import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    def before_map(self, map):
        controller = "ckanext.validation_schema_generator.controller:VSGController"

        map.connect(
            'validation_schema_generator.index',
            '/dataset/{dataset_id}/resource/{resource_id}/generate_schema',
            controller=controller,
            action='index',
            conditions=dict(method=['GET', 'POST']))

        return map
