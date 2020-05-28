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
  echo "> 4. ./scripts/workflow.sh release  | Prepare project for release"
  echo "> 5. ./scripts/workflow.sh help     | Display this help menu"
}

function check() {
  log_action "Checking if needed commands are installs"
  if [ "${1}" == "build" ]; then
    command_is_present "gcc"
    command_is_present "pip3"
    command_is_present "upx"
  fi
  if [ "${1}" == "test" ]; then
    command_is_present "pip3"
  fi
}

function build() {
  try "clean previous build" rm -rf build/ dist/
  try "install pip3 dependencies" pip3 install -r requirements.txt -r requirements-build.txt
  try "create a binary executable" pyinstaller templaty.spec
}

function test() {
  try "install pip3 dependencies" pip3 install -r requirements-tests.txt
  try "run tests" tox
}

function release() {
  current_version=$(grep -oP "__version__ = '(.*)'" "templaty/__init__.py" | grep -oP "[0-9\.-]+[a-z]*")
  echo "Current version: ${current_version}"
  echo -n "New version: "
  read -r new_version
  sed -i "s/${current_version}/${new_version}/g" "templaty/__init__.py"
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
