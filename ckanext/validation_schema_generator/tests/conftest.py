import pytest
from pytest_factoryboy import register

import ckan.tests.factories as factories


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


class SysadminFactory(factories.Sysadmin):
    pass


register(SysadminFactory, "sysadmin")
