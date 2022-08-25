from flask import Blueprint

import ckan.model as model
import ckan.plugins.toolkit as tk

vsg = Blueprint("validation_schema_generator", __name__)


@vsg.before_request
def before_request():
    try:
        context = dict(model=model, user=tk.g.user, auth_user_obj=tk.g.userobj)
        #TODO make proper check for editor, admin or sysadmin user
        tk.check_access(u'sysadmin', context)
    except tk.NotAuthorized:
        tk.abort(403, tk._(u'You are not allowed to generate resource schema'))


def index(dataset_id, resource_id):
    extra_vars = {
        "pkg_dict": tk.get_action("package_show")({}, {"id": dataset_id}),
        "resource": tk.get_action("resource_show")({}, {"id": resource_id}),
        "status": dict()
    }
    return tk.render('vsg/index.html', extra_vars=extra_vars)


vsg.add_url_rule(
    "/dataset/<dataset_id>/resource/<resource_id>/generate_schema",
    methods=["GET", "POST"],
    view_func=index,
)
