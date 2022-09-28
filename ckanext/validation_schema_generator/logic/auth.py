import ckan.plugins.toolkit as tk
import ckan.authz as authz


def _get_auth_functions():
    return {
        "vsg_generate": vsg_generate,
    }


def vsg_generate(context, data_dict):
    """Check if user is allowed to generate schema

    :param id: the id of the resource to generate schema for
    :type id: string
    """
    authorized = authz.is_authorized('resource_update', context,
                                     data_dict).get('success')

    if authorized:
        return {'success': True}

    msg = tk._('You are not authorized to generate schema for resource {}').format(
        data_dict['id']
    )
    return {'success': False, 'msg': msg}
