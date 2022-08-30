from ckan.logic.schema import validator_args


@validator_args
def vsg_status_schema(not_missing, resource_id_exists):
    return {"id": [not_missing, resource_id_exists]}
