import ckan.plugins.toolkit as tk


def _get_helpers():
    return {
        "vsg_get_apply_for_options": vsg_get_apply_for_options,
        "vsg_is_ckan_29": is_ckan_29
    }


def vsg_get_apply_for_options():
    return [
        {'value': '', 'text': ''},
        {'value': 'dataset', 'text': 'Dataset default'},
        {'value': 'resource', 'text': 'Resource'}
    ]


def is_ckan_29():
    """
    Returns True if using CKAN 2.9+, with Flask and Webassets.
    Returns False if those are not present.
    """
    return tk.check_ckan_version(min_version='2.9.0')
