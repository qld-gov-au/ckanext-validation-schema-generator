import json

from flask import Blueprint
from flask.views import MethodView
from tableschema import validate as ts_validate
from tableschema import ValidationError as TsValidationError

import ckan.plugins.toolkit as tk

from ckanext.validation_schema_generator.utils import (
    prepare_task_for_serialization, get_current_time, update_task)
from ckanext.validation_schema_generator.constants import (
    APPLY_FOR_OPTIONS, APPLY_FOR_DATASET, APPLY_FOR_RESOURCE, RES_SCHEMA_FIELD,
    PKG_SCHEMA_FIELD, APPLY_FOR_FIELD, EMPTY_SCHEMA, UNAPPLIED)

vsg = Blueprint("validation_schema_generator", __name__)


class VSGIndexView(MethodView):

    def _redirect(self, dataset_id, resource_id):
        return tk.h.redirect_to('validation_schema_generator.index',
                                dataset_id=dataset_id,
                                resource_id=resource_id)

    def get(self, dataset_id, resource_id):
        try:
            self.pkg_dict = tk.get_action(u'package_show')({}, {
                u'id': dataset_id
            })
            self.resource = tk.get_action(u'resource_show')({}, {
                u'id': resource_id
            })
        except tk.ObjectNotFound:
            return tk.abort(404, tk._(u'Resource not found'))
        except tk.NotAuthorized:
            return tk.abort(
                403, tk._(u'You are not allowed to generate resource schema'))

        try:
            task = tk.get_action(u'vsg_status')({}, {u'id': resource_id})
        except tk.NotAuthorized:
            return tk.abort(403, tk._(u'Not authorized to see this page'))

        if task.get('value'):
            self._clean_apply_for_if_missing(task)
            self._clean_if_applied_another_schema(task)

        return tk.render('vsg/index.html',
                         extra_vars={
                             "pkg_dict": self.pkg_dict,
                             "resource": self.resource,
                             "task": task
                         })

    def _clean_apply_for_if_missing(self, task):
        """If schema has been manually removed from package
        or resource -> reset apply_for, because it's definitely not applied
        """
        apply_for = task['value'].get(APPLY_FOR_FIELD)

        if not apply_for:
            return

        if apply_for == APPLY_FOR_DATASET:
            if not self.pkg_dict.get(PKG_SCHEMA_FIELD):
                task['value'][APPLY_FOR_FIELD] = UNAPPLIED
        elif apply_for == APPLY_FOR_RESOURCE:
            if not self.resource.get(RES_SCHEMA_FIELD):
                task['value'][APPLY_FOR_FIELD] = UNAPPLIED

        update_task({}, task.copy())

    def _clean_if_applied_another_schema(self, task):
        """If another generated from resource schema is applied, clear this one"""
        apply_for = task['value'].get(APPLY_FOR_FIELD)
        schema = json.loads(task['value'].get('schema') or '{}')

        if not apply_for or not schema:
            return

        if apply_for == APPLY_FOR_DATASET:
            if self.pkg_dict.get(PKG_SCHEMA_FIELD) and (
                    schema != self.pkg_dict.get(PKG_SCHEMA_FIELD)):
                task['value'][APPLY_FOR_FIELD] = UNAPPLIED
        elif apply_for == APPLY_FOR_RESOURCE:
            if not self.resource.get(RES_SCHEMA_FIELD) and (
                    schema != self.resource.get(RES_SCHEMA_FIELD)):
                task['value'][APPLY_FOR_FIELD] = UNAPPLIED

        update_task({}, task.copy())

    def post(self, dataset_id, resource_id):
        self.dataset_id = dataset_id
        self.resource_id = resource_id
        self.data = tk.request.form
        self.schema = self.data.get('schema')

        if 'generate' in self.data:
            try:
                tk.get_action(u'vsg_generate')({}, {"id": resource_id})
            except tk.ValidationError as e:
                tk.h.flash_error(e)
        elif 'apply' in self.data:
            self.apply_schema()

        return self._redirect(dataset_id, resource_id)

    def apply_schema(self):
        """Apply a generated schema for resource or dataset"""
        task = tk.get_action(u'vsg_status')({}, {u'id': self.resource_id})

        if not self._is_schema_valid():
            return

        apply_for = self.data[APPLY_FOR_FIELD]

        if not apply_for:
            applied_for = task['value'].get(APPLY_FOR_FIELD)
            task['value'][APPLY_FOR_FIELD] = ''

            if not applied_for:
                tk.h.flash_success(u"The schema is not applied yet")
            else:
                if applied_for == APPLY_FOR_DATASET:
                    self._unapply_package_schema()
                else:
                    self._unapply_resource_schema()
                tk.h.flash_success(u"The schema has been unapplied")
        else:
            if apply_for not in APPLY_FOR_OPTIONS:
                tk.h.flash_error(
                    u"Apply for {} not implemented".format(apply_for))
            else:
                if self.schema != task['value']['schema']:
                    task['last_updated'] = get_current_time()

                task['value'][APPLY_FOR_FIELD] = apply_for
                task['value']['schema'] = self.schema

                if apply_for == APPLY_FOR_DATASET:
                    self._apply_schema_for_pkg()
                else:
                    self._apply_res_schema()

        update_task({}, task)

    def _is_schema_valid(self):
        """Check if the schema is valid as the user could have changed
        it after generation"""
        valid = False

        try:
            ts_validate(json.loads(self.schema))
        except ValueError as e:
            tk.h.flash_error(e.message)
        except TsValidationError as e:
            for error in e.errors:
                tk.h.flash_error(error.message)
        else:
            valid = True

        return valid

    def _unapply_resource_schema(self):
        """Unapply resource schema actually means applying an empty one"""
        self.schema = EMPTY_SCHEMA
        self._apply_res_schema()

    def _apply_res_schema(self):
        """Apply the generated schema for resource and unapply for package"""
        res = tk.get_action(u'resource_show')({}, {u'id': self.resource_id})
        res[RES_SCHEMA_FIELD] = self.schema

        tk.get_action(u'resource_update')({}, res)

        self._unapply_package_schema()

    def _unapply_package_schema(self):
        """Unapply package schema actually means applying an empty one"""
        self.schema = EMPTY_SCHEMA
        self._apply_schema_for_pkg()

    def _apply_schema_for_pkg(self):
        """Apply the generated schema for package and unapply for resource"""
        pkg = tk.get_action(u'package_show')({}, {u'id': self.dataset_id})
        pkg[PKG_SCHEMA_FIELD] = self.schema

        if self.schema:
            for resource in pkg.get('resources', []):
                if resource['id'] == self.resource_id:
                    resource[RES_SCHEMA_FIELD] = ''

        tk.get_action(u'package_update')({}, pkg)


vsg.add_url_rule(
    "/dataset/<dataset_id>/resource/<resource_id>/generate_schema",
    methods=["GET", "POST"],
    view_func=VSGIndexView.as_view('index'),
)
