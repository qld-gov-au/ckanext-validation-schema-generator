import json

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.lib.jobs import enqueue as enqueue_job

import ckanext.validation_schema_generator.logic.schema as vsg_schema
from ckanext.validation_schema_generator import jobs, utils as vsg_utils, constants as const


def _get_actions():
    return {
        'vsg_generate': vsg_generate,
        'vsg_status': vsg_status,
        'vsg_update': vsg_update,
        'vsg_apply': vsg_apply,
        'vsg_unapply': vsg_unapply
    }


@validate(vsg_schema.vsg_generate_schema)
def vsg_generate(context, data_dict):
    """Generate a schema for a dataset

    :param id: resource ID
    :type id: string
    """
    tk.check_access('vsg_generate', context, data_dict)

    task = vsg_utils.update_task(
        context,
        vsg_utils.generate_task_data(data_dict["id"],
                                     const.TASK_STATE_PENDING))

    data = {"resource_id": data_dict["id"], "task_id": task["id"]}

    timeout = tk.asint(tk.config.get(
        const.CF_JOB_TIMEOUT, const.CF_JOB_TIMEOUT_DF))
    job = enqueue_job(jobs.generate_schema_from_resource, [data],
                      rq_kwargs={"timeout": timeout})

    task['value'] = {'job_id': job.id}
    task['error'] = {}

    return vsg_utils.update_task(context, task)


@validate(vsg_schema.vsg_default_schema)
def vsg_status(context, data_dict):
    """Return a status of schema generation for a specific resource

    :param id: resource ID
    :type id: string
    """
    tk.check_access('vsg_generate', context, data_dict)

    try:
        task = tk.get_action('task_status_show')(context, {
            'entity_id': data_dict["id"],
            'task_type': const.TASK_TYPE,
            'key': const.TASK_KEY
        })
    except tk.ObjectNotFound:
        return {
            'state': const.TASK_STATE_NOT_GENERATED,
            'last_updated': None,
            'value': None,
            'error': None
        }

    task['value'] = json.loads(task['value'])
    task['error'] = json.loads(task['error'])
    return task


@validate(vsg_schema.vsg_hook_schema)
def vsg_update(context, data_dict):
    """Hook to update vsg task from job"""
    id, error, status = tk.get_or_bust(data_dict, ['id', 'error', 'status'])

    tk.check_access('vsg_generate', context, {'id': id})
    task = tk.get_action('vsg_status')(context, {'id': id})

    task['state'] = status
    task['last_updated'] = vsg_utils.get_current_time()
    task['error'] = error

    if data_dict.get("schema"):
        task['value']['schema'] = json.loads(data_dict["schema"])

    return vsg_utils.update_task(context, task)


@validate(vsg_schema.vsg_apply_schema)
def vsg_apply(context, data_dict):
    """Apply a generated scheme or a new one. The scheme can be applied only
    if the generation process is successfully completed

    :param id: resource ID
    :type id: string
    :param apply_for: apply schema agaisnt the whole `dataset` or `resource` only.
    :type apply_for: string
    :param schema: if the schema is provided, it will replace the generated one (optional)
    :type schema: string
    """
    tk.check_access('vsg_generate', context, data_dict)

    apply_for = data_dict.get(const.APPLY_FOR_FIELD)
    schema = data_dict.get('schema')

    task = tk.get_action('vsg_status')(context, data_dict)

    if task['state'] in (const.TASK_STATE_NOT_GENERATED,
                         const.TASK_STATE_PENDING):
        raise tk.ValidationError(tk._(u"Schema is not generated yet."))
    elif task['state'] == const.TASK_STATE_ERROR:
        raise tk.ValidationError(
            tk._(u"Schema generation failed. Check status."))

    current_schema = task['value']['schema']

    if schema and current_schema != schema:
        task['last_updated'] = vsg_utils.get_current_time()

    schema = schema or current_schema

    task['value'][const.APPLY_FOR_FIELD] = apply_for

    task['value']['schema'] = vsg_utils.load_schema(schema)

    if apply_for == const.APPLY_FOR_DATASET:
        _apply_pkg_schema(schema, data_dict['id'])
    else:
        _apply_res_schema(schema, data_dict['id'])

    return vsg_utils.update_task(context, task)


def _apply_res_schema(schema, resource_id):
    """Apply the generated schema for resource and unapply for package"""
    context = {"user": "", "ignore_auth": True}

    res = tk.get_action(u'resource_show')(context, {u'id': resource_id})
    res[const.RES_SCHEMA_FIELD] = schema

    tk.get_action(u'resource_update')(context, res)


def _apply_pkg_schema(schema, resource_id):
    """Apply the generated schema for package and resource"""
    context = {"user": "", "ignore_auth": True}

    res = tk.get_action(u'resource_show')(context, {u'id': resource_id})
    pkg = tk.get_action(u'package_show')(context, {u'id': res['package_id']})

    pkg[const.PKG_SCHEMA_FIELD] = schema

    if schema:
        for resource in pkg.get('resources', []):
            if resource['id'] == resource_id:
                resource[const.RES_SCHEMA_FIELD] = schema

    tk.get_action(u'package_update')(context, pkg)


@validate(vsg_schema.vsg_default_schema)
def vsg_unapply(context, data_dict):
    """Unapply the schema
    """
    tk.check_access('vsg_generate', context, data_dict)

    task = tk.get_action('vsg_status')(context, data_dict)

    if task['state'] in (const.TASK_STATE_NOT_GENERATED,
                         const.TASK_STATE_PENDING):
        raise tk.ValidationError(u"Schema is not generated yet")
    elif task['state'] == const.TASK_STATE_ERROR:
        raise tk.ValidationError(u"Schema generation failed. Check status.")

    applied_for = task['value'].get(const.APPLY_FOR_FIELD)

    if not applied_for:
        raise tk.ValidationError(u"The schema is not applied yet")

    task['value'][const.APPLY_FOR_FIELD] = ''

    return vsg_utils.update_task(context, task)
