# encoding: utf-8

import requests

from frictionless import describe
from frictionless.errors import SchemaError

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.validation_schema_generator.constants import (
    CF_API_KEY,
    TASK_STATE_FINISHED,
    TASK_STATE_ERROR,
)


def generate_schema_from_resource(input):
    context = _make_context()

    resource = tk.get_action(u'resource_show')(context, {
        'id': input[u'resource_id']
    })

    errors = {}
    options = {}
    source = None
    schema = None

    if not source:
        source = resource[u'url']

    try:
        schema = describe(source, type='schema', **options)
    except SchemaError as e:
        errors[u'schema'] = str(e)
    except Exception as e:
        errors[u'undefined'] = str(e)
    finally:
        _update_task(input, errors, schema)


def _make_context():
    user = _get_site_user()

    return {
        'model': model,
        'session': model.Session,
        'ignore_auth': True,
        'user': user[u'name'],
        'auth_user_obj': None
    }


def _get_site_user():
    return tk.get_action(u'get_site_user')({
        'model': model,
        'ignore_auth': True
    }, {})


def _make_session():
    s = requests.Session()
    s.headers.update({u'Authorization': _get_api_key()})
    return s


def _get_api_key():
    return tk.config.get(CF_API_KEY, _get_site_user_api_key())


def _get_site_user_api_key():
    user = _get_site_user()
    return user['apikey']


def _update_task(input, errors, schema):
    context = _make_context()

    data_dict = {
        'id': input[u'resource_id'],
        'status': TASK_STATE_ERROR if errors else TASK_STATE_FINISHED,
        'error': errors,
        'schema': schema.to_json() if schema else ''
    }

    tk.get_action('vsg_update')(context, data_dict)
