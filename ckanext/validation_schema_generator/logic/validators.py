# encoding: utf-8

import ckan.plugins.toolkit as tk

import ckanext.validation_schema_generator.constants as const
from ckanext.validation_schema_generator.utils import validate_schema


def _get_validators():
    return {
        "vsg_validate_schema": vsg_validate_schema,
        "vsg_is_resource_supportable": vsg_is_resource_supportable,
        "vsg_resource_not_missing": vsg_resource_not_missing,
        "vsg_generation_started": vsg_generation_started
    }


def vsg_resource_not_missing(key, data, errors, context):
    """Check if resource with ID exists and force stop validation if not"""
    model = context['model']
    session = context['session']

    res = session.query(model.Resource).get(data[key])

    if not res:
        errors[key].append(tk._('Resource not found'))
        raise tk.StopOnError()


def vsg_is_resource_supportable(key, data, errors, context):
    """Checks if we're able to generate a schema for the resource
    Currently we are working only with resources that are inside the datastore
    just to be sure that it's a tabular data.

    In the future, we may also update this validator to perform comprehensive
    resource format/MIME type validation, which can be difficult.
    """
    model = context['model']
    session = context['session']

    res = session.query(model.Resource).get(data[key])

    if not res.extras.get('datastore_active'):
        errors[key].append(tk._('Schema couldn\'t be generated for this resource'))
        raise tk.StopOnError()


def vsg_validate_schema(value, context):
    """Validate table schema"""

    errors = validate_schema(value)

    for error in errors:
        raise tk.Invalid(error)

    return value


def vsg_generation_started(key, data, errors, context):
    """Checks if the vsg generation is started. Otherwise, there's no sense to update
    it somehow"""

    result = tk.get_action('vsg_status')(context, {"id": data[key]})

    if result['state'] == const.TASK_STATE_NOT_GENERATED:
        errors[key].append(tk._('The schema generation procecss isn\'t started yet.'))
        raise tk.StopOnError()
