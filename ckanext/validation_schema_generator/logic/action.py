import json

import ckan.plugins.toolkit as tk
from ckan.logic import validate

import ckanext.validation_schema_generator.jobs as jobs
from ckanext.validation_schema_generator.logic.schema import vsg_status_schema
from ckanext.validation_schema_generator.utils import generate_task_data, update_task, get_current_time
from ckanext.validation_schema_generator.constants import (
    TASK_KEY, TASK_STATE_NOT_GENERATED, TASK_TYPE, TASK_STATE_PENDING,
    CF_JOB_TIMEOUT, CF_JOB_TIMEOUT_DF)


def _get_actions():
    return {"vsg_generate": vsg_generate, "vsg_status": vsg_status, 'vsg_hook': vsg_hook}


@validate(vsg_status_schema)
def vsg_generate(context, data_dict):
    tk.check_access('vsg_generate', context, data_dict)

    task = update_task(context,
                       generate_task_data(data_dict["id"], TASK_STATE_PENDING))

    data = {"resource_id": data_dict["id"], "task_id": task["id"]}

    timeout = tk.asint(tk.config.get(CF_JOB_TIMEOUT, CF_JOB_TIMEOUT_DF))
    job = tk.enqueue_job(jobs.generate_schema_from_resource, [data],
                         rq_kwargs={"timeout": timeout})

    task['value'] = {'job_id': job.id}
    task['error'] = {}

    update_task(context, task)


@validate(vsg_status_schema)
def vsg_status(context, data_dict):
    tk.check_access('vsg_status', context, data_dict)

    try:
        task = tk.get_action('task_status_show')(context, {
            'entity_id': data_dict["id"],
            'task_type': TASK_TYPE,
            'key': TASK_KEY
        })
    except tk.ObjectNotFound:
        return {
            'state': TASK_STATE_NOT_GENERATED,
            'last_updated': None,
            'value': None,
            'error': None
        }

    task['value'] = json.loads(task['value'])
    task['error'] = json.loads(task['error'])
    return task


def vsg_hook(context, data_dict):
    id, error, status = tk.get_or_bust(data_dict, ['id', 'error', 'status'])

    tk.check_access('vsg_generate', context, {'id': id})
    task = tk.get_action('vsg_status')(context, {'id': id})

    task['state'] = status
    task['last_updated'] = get_current_time()
    task['error'] = error
    task['value']['schema'] = data_dict.get("schema", "")

    update_task(context, task)
