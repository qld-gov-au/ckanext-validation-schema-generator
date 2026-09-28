# encoding: utf-8

import pytest

import ckan.plugins.toolkit as tk
import ckan.model as model
from ckan.tests import helpers, factories


@pytest.mark.usefixtures("with_plugins")
class TestAuth(object):

    def test_anon_not_allowed(self, new_resource):
        resource = new_resource()
        context = {"user": "", "model": model}

        with pytest.raises(tk.NotAuthorized):
            helpers.call_auth("vsg_generate", context, id=resource["id"])

    def test_regular_user_not_allowed(self, new_resource):
        resource = new_resource()
        user = factories.User()
        context = {"user": user["name"], "model": model}

        with pytest.raises(tk.NotAuthorized):
            helpers.call_auth("vsg_generate", context, id=resource["id"])

    def test_sysadmin(self, new_dataset, new_resource):
        resource = new_resource()
        user = factories.Sysadmin()
        context = {"user": user["name"], "model": model}
        helpers.call_auth("vsg_generate",
                          context,
                          id=resource["id"])
