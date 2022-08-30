import json
from datetime import datetime as dt

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


def prepare_task_for_serialization(task):
    task['value'] = json.dumps(task['value'])
    task['error'] = json.dumps(task['error'])
    return task

def update_task(context, data_dict):
    prepare_task_for_serialization(data_dict)

    context["ignore_auth"] = True
    return tk.get_action('task_status_update')(
        context,
        data_dict
    )
