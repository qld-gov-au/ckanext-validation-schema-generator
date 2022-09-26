# encoding: utf-8

import pytest

import ckan.plugins.toolkit as tk
from ckan.tests import helpers, factories

import ckanext.validation_schema_generator.constants as const


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestActionGenerate(object):

    def test_not_in_datastore(self):
        resource = factories.Resource()
        err_msg = u"Schema couldn't be generated for this resource"

        with pytest.raises(tk.ValidationError, match=err_msg):
            helpers.call_action('vsg_generate', id=resource['id'])

    def test_in_datastore(self):
        resource = factories.Resource(datastore_active=True)
        result = helpers.call_action('vsg_generate', id=resource['id'])

        assert result["entity_id"] == resource["id"]
        assert result["task_type"] == const.TASK_TYPE
        assert result["entity_type"] == "resource"
        assert result["value"]["job_id"]
        assert result["state"] == const.TASK_STATE_PENDING
        assert result["key"] == const.TASK_KEY

    def test_missing_resource(self):
        with pytest.raises(tk.ValidationError, match='Resource not found'):
            helpers.call_action('vsg_generate', id='missing')

    def test_res_id_not_provided(self):
        with pytest.raises(tk.ValidationError, match='Missing value'):
            helpers.call_action('vsg_generate')


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestActionStatus(object):

    def test_generation_started(self):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])
        result = helpers.call_action('vsg_status', id=resource["id"])

        assert result["entity_id"] == resource["id"]
        assert result["task_type"] == const.TASK_TYPE
        assert result["entity_type"] == "resource"
        assert result["value"]["job_id"]
        assert result["state"] == const.TASK_STATE_PENDING
        assert result["key"] == const.TASK_KEY

    def test_not_generated(self):
        resource = factories.Resource()
        result = helpers.call_action('vsg_status', id=resource["id"])

        assert result['state'] == const.TASK_STATE_NOT_GENERATED
        assert not result['error']
        assert not result['value']
        assert not result['last_updated']

    def test_res_id_not_provided(self):
        with pytest.raises(tk.ValidationError, match='Missing value'):
            helpers.call_action('vsg_status')


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestActionApply(object):

    def test_apply_for_wrong_entity(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])

        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)

        with pytest.raises(tk.ValidationError):
            helpers.call_action('vsg_apply',
                                id=resource["id"],
                                apply_for="organization",
                                schema=table_schema)

    def test_apply_for_resource(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)
        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_RESOURCE,
                            schema=table_schema)

        resource = helpers.call_action("resource_show", id=resource["id"])
        assert resource[const.RES_SCHEMA_FIELD]

    def test_apply_for_package(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)
        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_DATASET,
                            schema=table_schema)

        pkg = helpers.call_action("package_show", id=resource["package_id"])
        assert pkg[const.PKG_SCHEMA_FIELD]

    def test_apply_resource_must_unapply_pkg_schema(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)
        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_RESOURCE,
                            schema=table_schema)

        resource = helpers.call_action("resource_show", id=resource["id"])
        assert resource[const.RES_SCHEMA_FIELD]

        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_DATASET,
                            schema=table_schema)

        pkg = helpers.call_action("package_show", id=resource["package_id"])
        assert pkg[const.PKG_SCHEMA_FIELD]
        assert not pkg['resources'][0][const.RES_SCHEMA_FIELD]

    def test_apply_pkg_must_unapply_resource_schema(self, table_schema):
        resource = factories.Resource(datastore_active=True)

        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)
        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_DATASET,
                            schema=table_schema)

        pkg = helpers.call_action("package_show", id=resource["package_id"])
        assert pkg[const.PKG_SCHEMA_FIELD]

        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_RESOURCE,
                            schema=table_schema)

        resource = helpers.call_action("resource_show", id=resource["id"])
        pkg = helpers.call_action("package_show", id=resource["package_id"])

        assert not pkg[const.PKG_SCHEMA_FIELD]
        assert resource[const.RES_SCHEMA_FIELD]


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestActionUnapply(object):

    def test_unapply(self, table_schema):
        resource = factories.Resource(datastore_active=True)

        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)
        helpers.call_action('vsg_apply',
                            id=resource["id"],
                            apply_for=const.APPLY_FOR_RESOURCE,
                            schema=table_schema)

        resource = helpers.call_action("resource_show", id=resource["id"])
        assert resource[const.RES_SCHEMA_FIELD]

        helpers.call_action('vsg_unapply', id=resource["id"])

        resource = helpers.call_action("resource_show", id=resource["id"])
        assert not resource[const.RES_SCHEMA_FIELD]

    def test_unapply_not_applied(self, table_schema):
        resource = factories.Resource(datastore_active=True)

        helpers.call_action('vsg_generate', id=resource['id'])
        helpers.call_action('vsg_update',
                            id=resource["id"],
                            status=const.TASK_STATE_FINISHED,
                            error={},
                            schema=table_schema)

        with pytest.raises(tk.ValidationError):
            helpers.call_action('vsg_unapply', id=resource["id"])


@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestActionHook(object):

    def test_success(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        result = helpers.call_action('vsg_generate', id=resource['id'])

        assert result["state"] == const.TASK_STATE_PENDING

        result = helpers.call_action('vsg_update',
                                     id=resource["id"],
                                     status=const.TASK_STATE_FINISHED,
                                     error={},
                                     schema=table_schema)

        assert result["entity_id"] == resource["id"]
        assert result["state"] == const.TASK_STATE_FINISHED
        assert result['value']['schema']

    def test_not_started(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        err_msg = u"The schema generation procecss isn't started yet."

        with pytest.raises(tk.ValidationError, match=err_msg):
            helpers.call_action('vsg_update',
                                id=resource["id"],
                                status=const.TASK_STATE_FINISHED,
                                error={},
                                schema=table_schema)

    def test_wrong_state(self, table_schema):
        resource = factories.Resource(datastore_active=True)
        helpers.call_action('vsg_generate', id=resource['id'])

        with pytest.raises(tk.ValidationError):
            helpers.call_action('vsg_update',
                                id=resource["id"],
                                status="active",
                                error={},
                                schema=table_schema)
