import pytest


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
