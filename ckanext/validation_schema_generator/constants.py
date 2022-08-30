TASK_TYPE = u"generate"
TASK_KEY = u"validation_schema_generator"
TASK_STATE_PENDING = u"Pending"
TASK_STATE_FINISHED = u"Finished"
TASK_STATE_NOT_GENERATED = u"Not generated"
TASK_STATE_ERROR = u"Failed"

CF_JOB_TIMEOUT = u"ckanext.validation_schema_generator.job_timeout"
CF_JOB_TIMEOUT_DF = 3600
CF_PASS_AUTH = u"ckanext.validation_schema_generator.pass_api_key"
CF_PASS_AUTH_DF = True
CF_API_KEY = u"ckanext.validation_schema_generator.api_key"

APPLY_FOR_OPTIONS = (u"dataset", u"resource")
APPLY_FOR_DATASET = APPLY_FOR_OPTIONS[0]
APPLY_FOR_RESOURCE = APPLY_FOR_OPTIONS[1]
APPLY_FOR_FIELD = u"apply_for"

RES_SCHEMA_FIELD = u"schema"
PKG_SCHEMA_FIELD = u"default_data_schema"

EMPTY_SCHEMA = u""
UNAPPLIED = u""
