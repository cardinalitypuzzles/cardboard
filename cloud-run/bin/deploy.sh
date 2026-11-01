#!/bin/bash
set -eo pipefail

# https://mikefarah.gitbook.io/yq

cd cloud-run

export MY_YQ_CLOUDSQL_INSTANCE="$CARDBOARD_CR_DB_INSTANCE"
export MY_YQ_SERVICE_ACCOUNT="$CARDBOARD_CR_SERVICE_ACCOUNT"
export MY_YQ_IMAGE="$CARDBOARD_CR_DOCKER_REPOSITORY:$1"

MY_COMMAND='.'
MY_COMMAND="$MY_COMMAND"' | .spec.template.spec.containers[].env = load(".env.yaml")'
MY_COMMAND="$MY_COMMAND"' | .spec.template.metadata.annotations."run.googleapis.com/cloudsql-instances" = strenv(MY_YQ_CLOUDSQL_INSTANCE)'
MY_COMMAND="$MY_COMMAND"' | .spec.template.spec.serviceAccountName = strenv(MY_YQ_SERVICE_ACCOUNT)'
MY_COMMAND="$MY_COMMAND"' | .spec.template.spec.containers[].image = strenv(MY_YQ_IMAGE)'

yq "$MY_COMMAND" service.yaml > .service.yaml

# .spec.template.metadata.annotations."run.googleapis.com/cloudsql-instances"
# .spec.template.spec.serviceAccountName
# .spec.template.spec.containers[].image


gcloud --project="$CARDBOARD_CR_PROJECT" run services replace .service.yaml
