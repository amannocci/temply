#!/usr/bin/env bash

# Found current script directory
RELATIVE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Load common
# shellcheck disable=SC1090
source "${RELATIVE_DIR}/common.sh"

function help() {
  echo "-- Help Menu"
  echo "> 1. ./scripts/workflow.sh build    | Build the project"
  echo "> 2. ./scripts/workflow.sh test     | Run tests on this project"
  echo "> 3. ./scripts/workflow.sh release  | Prepare project for release"
  echo "> 4. ./scripts/workflow.sh help     | Display this help menu"
}

function check() {
  log_action "Checking if needed commands are installs"
  if [ "${1}" == "build" ]; then
    command_is_present "gcc"
    command_is_present "pip3"
    command_is_present "upx"
    command_is_present "python3.6"
  fi
  if [ "${1}" == "test" ]; then
    command_is_present "pip3"
    command_is_present "python3.6"
  fi
}

function setup() {
  # Constants
  HOOK_DIR=${BASE_PROJECT}/.git/hooks

  # Create directory
  mkdir -p "${HOOK_DIR}"

  # Remove all old hooks before anything
  log_success "remove old hooks"
  rm -f "${HOOK_DIR}/commit-msg"
  rm -f "${HOOK_DIR}/pre-commit"

  # Copy new ones
  log_success "copy new hooks"
  cp "${RELATIVE_DIR}/hook-commit-msg.sh" "${HOOK_DIR}/commit-msg"
  cp "${RELATIVE_DIR}/hook-pre-commit.sh" "${HOOK_DIR}/pre-commit"
}

function build() {
  try "clean previous build" rm -rf build/ dist/
  try "install pip3 dependencies" pip3 install -r requirements.txt -r requirements-build.txt
  try "create a binary executable" pyinstaller temply.spec
}

function test() {
  try "install pip3 dependencies" pip3 install -r requirements-tests.txt
  try "run tests" tox
}

function release() {
  current_version=$(grep -oP "__version__ = '(.*)'" "temply/__init__.py" | grep -oP "[0-9\.-]+[a-z]*")
  echo "Current version: ${current_version}"
  echo -n "New version: "
  read -r new_version
  sed -i "s/${current_version}/${new_version}/g" "temply/__init__.py"
}

# Parse argument
arg="${1}"
if [[ -z "${arg}" ]] ; then
  echo "Expected arg to be present"
  help
else
  case "${arg}" in
    help)
      help
      ;;
    setup)
      setup
      ;;
    build)
      check "build"
      build
      ;;
    test)
      check "test"
      test
      ;;
    release)
      release
      ;;
    *)
      echo "Unknown argument: ${arg}"
      help
      ;;
  esac
fi
