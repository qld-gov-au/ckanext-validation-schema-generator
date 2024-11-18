# encoding: utf-8

def _get_helpers():
    return {
        "vsg_get_apply_for_options": vsg_get_apply_for_options
    }


def vsg_get_apply_for_options():
    return [
        {'value': '', 'text': ''},
        {'value': 'dataset', 'text': 'Dataset default'},
        {'value': 'resource', 'text': 'Resource'}
    ]
