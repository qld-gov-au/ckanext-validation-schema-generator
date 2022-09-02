# ckanext-validation-schema-generator

This extension helps to generate table schema for a resource based on its content. Support tabular data.
You must define a field for datasets and resources to store a table schema data. Check config options below.


## Requirements

This extension has been written to work with python 2 and CKAN 2.9.5. Relies on datastore.

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9.5+           | yes          |

Suggested values:

* "yes"
* "not tested" - I can't think of a reason why it wouldn't work
* "not yet" - there is an intention to get it working
* "no"


## Installation

**TODO:** Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-validation-schema-generator:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-validation-schema-generator.git
    cd ckanext-validation-schema-generator
    pip install -e .
	pip install -r requirements.txt

3. Add `validation-schema-generator` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

    # The maximum time for the schema generation before it is aborted.
    # Give an amount in seconds. Default is 60 minutes
    # (optional, default: 3600).
    ckanext.validation_schema_generator.job_timeout = 3600

    # If the resource is remote or private, we could pass an API key inside headers
    # This option defines should we pass API key or not
    # (optional, default: True).
    ckanext.validation_schema_generator.pass_api_key = True

    # API key that is going to be passed for `Authorization`
    ckanext.validation_schema_generator.api_key =

    # Field name for dataset schema field
    # (optional, default: schema)
    ckanext.validation_schema_generator.resource_schema_field_name = schema

    # Field name for dataset schema field
    # (optionak, default: schema)
    ckanext.validation_schema_generator.package_schema_field_name = default_data_schema


## Developer installation

To install ckanext-validation-schema-generator for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-validation-schema-generator.git
    cd ckanext-validation-schema-generator
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

There are few tests for the extension, so you could run it with next command. Be sure, that you've installed the dev-requirements from CKAN.

    pytest --ckan-ini=test.ini


## API endpoints

The extension has next endpoints to manipulate the schema generation process.

1. `vsg_generate` - starts the schema generation process by creating the appropriate task, queues a background job to be executed by `ckan jobs worker`.
    **Params**:
    - `id` _(required)_ - ID of the resource. Resource must be stored inside the datastore.

    **Returns**
    ```
    {
      "help": ".../api/3/action/help_show?name=vsg_generate",
      "success": true,
      "result": {
        "entity_id": "<RESOURCE_ID>",
        "task_type": "generate",
        "last_updated": "2022-09-02 14:21:14.543511",
        "entity_type": "resource",
        "value": {
          "job_id": "<JOB_ID>"
        },
        "state": "Pending",
        "key": "validation_schema_generator",
        "error": "{}",
        "id": "<TASK_ID>"
      }
    }

2. `vsg_status` - returns a status of schema generation for a specific resource.
    **Params**:
    - `id` _(required)_ - ID of the resource

    **Returns**:
    ```
    {
      "help": ".../api/3/action/help_show?name=vsg_status",
      "success": true,
      "result": {
        "entity_id": "<RESOURCE_ID>",
        "task_type": "generate",
        "last_updated": "2022-09-02T14:21:18.289917",
        "entity_type": "resource",
        "value": {
          "job_id": "<JOB_ID>",
          "schema": {
            "fields": [
              {
                "type": "string",
                "name": "Name",
                "format": "default"
              }
              ...
            ]
        },
        "state": "Finished",
        "key": "validation_schema_generator",
        "error": {},
        "id": "<TASK_ID>"
      }
    }

3. `vsg_update` - updates a schema generation task data. The background job uses this action to update task after the schema is generated. Could be used for a testing purposes.
    **Params**:
    - `id` _(required)_ - ID of the resource. The generation process must be in progress, otherwise returns a validation error.
    - `error` _(required)_ - A dict of errors, e.g. `{'format': 'couldn't generate a schema for XXX format'}`.
    - `status` _(required)_- status of a task, must be one of `["Pending", "Finished", "Failed"]`
    - `schema` _(optional)_ - a table schema, [read more about it](https://specs.frictionlessdata.io//table-schema/)

    **Returns**
    Updated task data, same as `vsg_status`

4. `vsg_apply` - Apply a generated scheme or a new one. The scheme can be applied only if the generation process is successfully completed.
    **params**:
    - `id` (required) - ID of the resource
    - `apply_for` _(required)_- apply for entity, must be one of `["dataset", "resource"]`
    - `schema` _(optional)_ - a table schema. If not provided, the generated one will be used.

5. `vsg_unapply` - Unapply the schema. Automatically clears the dataset/resource schema if it was using the generated schema.
    **params**:
    - `id` (required) - ID of the resource

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
