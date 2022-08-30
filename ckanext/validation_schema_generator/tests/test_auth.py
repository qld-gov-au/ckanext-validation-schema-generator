import pytest
import mock

import ckan.logic as logic
import ckan.model as model
from ckan.tests import helpers, factories


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestAuth(object):

    def test_anon_not_allowed(self):
        resource = factories.Resource()
        context = {"user": "", "model": model}

        with pytest.raises(logic.NotAuthorized):
            helpers.call_auth("vsg_generate", context, id=resource["id"])

    # TODO: Problem with auth for regualar user
    # def test_regular_user_not_allowed(self):
    #     resource = factories.Resource()
    #     user = factories.User()
    #     context = {"user": user["name"], "model": model}

    #     with pytest.raises(logic.NotAuthorized):
    #         helpers.call_auth("vsg_generate", context, id=resource["id"])

    def test_sysadmin(self):
        user = factories.Sysadmin()
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org["id"])
        resource = factories.Resource(package_id=dataset["id"])

        context = {"user": user["name"], "model": model}
        helpers.call_auth("vsg_generate",
                                     context,
                                     id=resource["id"])
