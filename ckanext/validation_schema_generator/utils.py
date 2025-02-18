# encoding: utf-8

from datetime import datetime as dt
import json

from frictionless import Schema
from frictionless.errors import SchemaError

import ckan.plugins.toolkit as tk

from .constants import TASK_TYPE, TASK_KEY


def generate_task_data(resource_id, state):
    return {
        'entity_id': resource_id,
        'entity_type': 'resource',
        'task_type': TASK_TYPE,
        'last_updated': get_current_time(),
        'state': state,
        'key': TASK_KEY,
        'value': {},
        'error': {},
    }


def get_current_time():
    return str(dt.utcnow())


def update_task(context, data_dict):
    context["ignore_auth"] = True

    data_dict['value'] = json.dumps(data_dict['value'])
    data_dict['error'] = json.dumps(data_dict['error'])

    task = tk.get_action('task_status_update')(context, data_dict)

    task['value'] = json.loads(task['value'])

    return task


def validate_schema(schema):
    """Validate the table schema and returns an array of errors"""
    errors = []

    try:
        Schema.from_descriptor(json.loads(schema))
    except ValueError as e:
        errors.append(e.message)
    except SchemaError as e:
        for error in e.errors:
            errors.append(error.message)

    return errors


def load_schema(value):
    """If the schema is JSON string - loads it and return,
    if not - return it as is"""

    try:
        value = json.loads(value)
    except (TypeError, ValueError):
        return value

    return value


def dump_schema(value):
    """Dump schema if dict, else return as is"""

    if isinstance(value, dict):
        return json.dumps(value)

    return value
