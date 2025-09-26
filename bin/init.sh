#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

. "${APP_DIR}"/bin/activate
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
ckan_cli datastore set-permissions | psql "postgresql://datastore_write:pass@postgres-datastore/datastore_test" --set ON_ERROR_STOP=1

