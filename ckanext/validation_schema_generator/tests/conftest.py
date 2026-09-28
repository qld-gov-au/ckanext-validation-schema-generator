import pytest

from ckan.tests import factories


@pytest.fixture
def new_dataset():
    def dataset_with_defaults(**kwargs):
        args = {
            'author_email': 'example@example.com',
            'license_id': 'other-open',
            'version': '1.0'
        }
        args.update(kwargs)
        if 'owner_org' not in kwargs:
            org = factories.Organization()
            args['owner_org'] = org['id']
        return factories.Dataset(**args)
    return dataset_with_defaults


@pytest.fixture
def new_resource(new_dataset):
    def resource_with_defaults(**kwargs):
        if 'package_id' not in kwargs:
            dataset = new_dataset()
            kwargs['package_id'] = dataset['id']
        return factories.Resource(**kwargs)
    return resource_with_defaults


@pytest.fixture
def table_schema():
    return '''{
        "fields": [{
            "type": "integer",
            "name": "Postcode",
            "format": "default"
        }, {
            "type": "integer",
            "name": "Sales_Rep_ID",
            "format": "default"
        }, {
            "type": "string",
            "name": "Sales_Rep_Name",
            "format": "default"
        }, {
            "type": "integer",
            "name": "Year",
            "format": "default"
        }, {
            "type": "number",
            "name": "Value",
            "format": "default"
        }],
        "missingValues": [""]
    }'''
