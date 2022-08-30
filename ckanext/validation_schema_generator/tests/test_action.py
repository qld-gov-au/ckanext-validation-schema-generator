import pytest
import mock

from ckan.tests import helpers, factories


@pytest.mark.usefixtures("clean_db", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "datastore xloader")
class TestAction(object):
    pass
    #TODO: implement action tests
    # def test_submit(self):
    #     # checks that xloader_submit enqueues the resource (to be xloadered)
    #     user = factories.User()
    #     # normally creating a resource causes xloader_submit to be called,
    #     # but we avoid that by setting an invalid format
    #     res = factories.Resource(user=user, format="aaa")
    #     # mock the enqueue
    #     with mock.patch(
    #         "ckanext.xloader.action.enqueue_job",
    #         return_value=mock.MagicMock(id=123),
    #     ) as enqueue_mock:
    #         helpers.call_action(
    #             "xloader_submit",
    #             context=dict(user=user["name"]),
    #             resource_id=res["id"],
    #         )
    #         assert 1 == enqueue_mock.call_count


    # def test_xloader_hook(self):
    #     # Check the task_status is stored correctly after a xloader job.
    #     user = factories.User()
    #     res = factories.Resource(user=user, format="csv")
    #     task_status = helpers.call_action(
    #         "task_status_update",
    #         context={},
    #         entity_id=res["id"],
    #         entity_type="resource",
    #         task_type="xloader",
    #         key="xloader",
    #         value="{}",
    #         error="{}",
    #         state="pending",
    #     )

    #     helpers.call_action(
    #         "xloader_hook",
    #         context=dict(user=user["name"]),
    #         metadata={"resource_id": res["id"]},
    #         status="complete",
    #     )

    #     task_status = helpers.call_action(
    #         "task_status_show",
    #         context={},
    #         entity_id=res["id"],
    #         task_type="xloader",
    #         key="xloader",
    #     )
    #     assert task_status["state"] == "complete"

    # def test_status(self):

    #     # Trigger an xloader job
    #     res = factories.Resource(format="CSV")

    #     status = helpers.call_action(
    #         "xloader_status",
    #         resource_id=res["id"],
    #     )

    #     assert status['status'] == 'pending'
