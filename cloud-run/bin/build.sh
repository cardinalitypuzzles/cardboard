#!/bin/bash
set -eo pipefail

# Requires https://mikefarah.gitbook.io/yq

MY_VERSION="v$(printf '%(%Y%m%d%H%M%S)T')"
MY_IMAGE="$CARDBOARD_CR_DOCKER_REPOSITORY:$MY_VERSION"

# Set package-mode to true because the Dockerfile uses poetry build
yq -p toml -o toml '.tool.poetry.package-mode = true' pyproject.toml > cloud-run/.pyproject.toml

docker build -t cardboard -f cloud-run/Dockerfile .
docker tag cardboard "$MY_IMAGE"
docker push "$MY_IMAGE"

echo
echo "./cloud-run/bin/deploy.sh $MY_VERSION"
