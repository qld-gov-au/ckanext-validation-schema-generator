# encoding: utf-8

from ckan.lib.base import BaseController
import ckan.plugins.toolkit as tk

from ckanext.validation_schema_generator.views import VSGIndexView


class VSGController(BaseController):
    def _check_access(self, resource_id):
        try:
            tk.check_access('vsg_generate', {}, {"id": resource_id})
        except tk.NotAuthorized:
            tk.abort(403, tk._(u'You are not allowed to generate resource schema'))

    def index(self, dataset_id, resource_id):
        self._check_access(resource_id)

        view = VSGIndexView()

        if tk.request.method == 'GET':
            return view.get(dataset_id, resource_id)

        return view.post(dataset_id, resource_id)
