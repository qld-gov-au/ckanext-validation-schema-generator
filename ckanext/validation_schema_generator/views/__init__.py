import json
from ckan.plugins.toolkit import ValidationError

from flask import Blueprint
from flask.views import MethodView

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk

from ckanext.validation_schema_generator.utils import update_task
from ckanext.validation_schema_generator.constants import (
    APPLY_FOR_DATASET,
    APPLY_FOR_RESOURCE,
    RES_SCHEMA_FIELD,
    PKG_SCHEMA_FIELD,
    APPLY_FOR_FIELD,
    UNAPPLIED,
)

vsg = Blueprint("validation_schema_generator", __name__)


class VSGIndexView(MethodView):

    def _redirect(self, dataset_id, resource_id):
        return h.redirect_to('validation_schema_generator.index',
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

        if task.get('value') and task['value'].get('schema'):
            task['value']['schema'] = self._format_schema(
                task['value']['schema'])

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
        schema = task['value'].get('schema')

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

    def _format_schema(self, schema):
        return json.dumps(schema, indent=4)

    def post(self, dataset_id, resource_id):
        self.dataset_id = dataset_id
        self.resource_id = resource_id
        self.data = tk.request.form
        self.schema = self.data.get('schema')

        if 'generate' in self.data:
            try:
                tk.get_action(u'vsg_generate')({}, {"id": resource_id})
            except tk.ValidationError as e:
                h.flash_error(str(e))
        elif 'apply' in self.data:
            self.apply_schema()

        return self._redirect(dataset_id, resource_id)

    def apply_schema(self):
        """Apply a generated schema for a resource or dataset"""

        apply_for = self.data[APPLY_FOR_FIELD]

        if not apply_for:
            try:
                tk.get_action(u'vsg_unapply')({}, {"id": self.resource_id})
            except ValidationError as e:
                return h.flash_error(_fetch_error(e))
            else:
                return h.flash_success(tk._(u"The schema has been unapplied"))

        try:
            tk.get_action(u'vsg_apply')({}, {
                "id": self.resource_id,
                "schema": self.schema,
                "apply_for": apply_for
            })
        except ValidationError as e:
            return h.flash_error(_fetch_error(e))
        else:
            return h.flash_error(
                tk._(u"The schema has been applied for {}").format(apply_for))


def _fetch_error(e):
    for err in e.error_dict.values():
        if isinstance(err, list):
            return err[0]
        return err


vsg.add_url_rule(
    "/dataset/<dataset_id>/resource/<resource_id>/generate_schema",
    methods=["GET", "POST"],
    view_func=VSGIndexView.as_view('index'),
)
