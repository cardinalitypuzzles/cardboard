#!/bin/bash
set -eo pipefail

MY_VERSION="v$(printf '%(%Y%m%d%H%M%S)T')"
MY_IMAGE="$CARDBOARD_CR_DOCKER_REPOSITORY:$MY_VERSION"

docker build -t cardboard -f cloud-run/Dockerfile .
docker tag cardboard "$MY_IMAGE"
docker push "$MY_IMAGE"

echo
echo "./cloud-run/bin/deploy.sh $MY_VERSION"
