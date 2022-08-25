# encoding: utf-8

from ckan.lib.base import BaseController
import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.validation_schema_generator.views import index


class VSGController(BaseController):

    def __before__(self, action, **params):
        super(VSGController, self).__before__(action, **params)

        context = {
            'model': model,
            'user': tk.c.user,
            'auth_user_obj': tk.c.userobj
        }

        try:
            #TODO make proper check for editor, admin or sysadmin user
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._(u'You are not allowed to generate resource schema'))

    def index(self, dataset_id, resource_id):
        return index(dataset_id, resource_id)
