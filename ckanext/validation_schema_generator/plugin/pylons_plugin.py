# -*- coding: utf-8 -*-

import ckan.plugins as p


class VSGMixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes)

    def before_map(self, map):
        controller = "ckanext.validation_schema_generator.controller:VSGController"

        map.connect(
            '/dataset/{dataset_id}/resource/{resource_id}/generate_schema',
            controller=controller,
            action='index',
            conditions=dict(method=['GET', 'POST']))

        # map.connect('data_qld_reporting.index', '/dashboard/reporting', controller=controller, action='index')
        return map
