# encoding: utf-8

from ckan.logic.schema import validator_args

import ckanext.validation_schema_generator.constants as const


@validator_args
def vsg_default_schema(not_missing, vsg_resource_not_missing):
    return {"id": [not_missing, vsg_resource_not_missing]}


@validator_args
def vsg_generate_schema(not_missing, vsg_is_resource_supportable,
                        vsg_resource_not_missing):
    return {
        "id":
        [not_missing, vsg_resource_not_missing, vsg_is_resource_supportable]
    }


@validator_args
def vsg_apply_schema(not_missing, resource_id_exists, one_of):
    return {
        "id": [not_missing, resource_id_exists],
        "apply_for": [not_missing, one_of(const.APPLY_FOR_OPTIONS)]
    }


@validator_args
def vsg_hook_schema(not_missing, resource_id_exists, one_of, ignore_missing,
                    vsg_validate_schema, unicode_safe, dict_only,
                    vsg_is_resource_supportable, vsg_generation_started):

    return {
        "id": [
            not_missing, resource_id_exists, vsg_is_resource_supportable,
            vsg_generation_started
        ],
        "error": [not_missing, dict_only],
        "status": [not_missing, one_of(const.VALID_STATES)],
        "schema": [ignore_missing, unicode_safe, vsg_validate_schema]
    }
