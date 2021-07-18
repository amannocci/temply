#!/usr/bin/env bash

# Found current script directory
RELATIVE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Load common
# shellcheck disable=SC1090
source "${RELATIVE_DIR}/../../scripts/lib.sh"

# Constants
if [[ $BASE_PROJECT == *".git"* ]]; then
  BASE_PROJECT=$(dirname "$BASE_PROJECT")
fi
cd "${BASE_PROJECT}" || exit 1

# Validate new version
HOOK_DIR=${BASE_PROJECT}/.git/hooks
if [ "$(diff "${BASE_PROJECT}/scripts/hook-pre-commit.sh" "${HOOK_DIR}/pre-commit" | wc -l)" -ne 0 ]; then
  log::failure "use current version of scripts\nPlease run './scripts/workflow.sh' setup again !"
  exit 1
fi

# Validate project
process::try "test project" "${BASE_PROJECT}/scripts/workflow.sh" test
log::success "validate project"
