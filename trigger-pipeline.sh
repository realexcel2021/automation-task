#!/bin/bash

# trigger the gihub actions build
TRIGGER_BUILD=$(curl --silent --include -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer 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" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/realexcel2021/automation-task/actions/workflows/build-image.yml/dispatches \
  -d '{"ref":"master"}')

# retireve the build status
BUILD_RES=$(echo "$TRIGGER_BUILD" | awk '/^HTTP/{print $2}')

echo $BUILD_RES 

BUILD_RES2=204

if [$BUILD_RES2 -eq 204]; then
  echo "Build trigger was successfull"
else
  echo "Build trigger was not successfull"
fi


# curl -X POST https://hub.docker.com/v2/users/login \
#   -H 'Content-Type: application/json'\
#   -d '{"username": "sheriffexcel", "password": "Thinkso109159381912"}'