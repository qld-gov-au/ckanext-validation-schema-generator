import ckan.plugins.toolkit as tk
import ckan.authz as authz


def _get_auth_functions():
    return {"vsg_generate": vsg_generate, "vsg_status": vsg_status}


def vsg_generate(context, data_dict):
    """Check if user is allowed to generate schema

    :param id: the id of the resource to generate schema for
    :type id: string
    """
    return authz.is_authorized("resource_update", context, data_dict)


def vsg_status(context, data_dict):
    """Check if user is allowed to check VSG status

    :param id: the id of the resource to check vsg status
    :type id: string
    """
    return authz.is_authorized("resource_update", context, data_dict)
