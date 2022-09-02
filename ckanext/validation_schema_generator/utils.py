import json
from datetime import datetime as dt

from tableschema import validate as ts_validate
from tableschema import ValidationError as TsValidationError

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
        ts_validate(json.loads(schema))
    except ValueError as e:
        errors.append(e.message)
    except TsValidationError as e:
        for error in e.errors:
            errors.append(error.message)

    return errors
