#!/usr/bin/env bash

# Found current script directory
export RELATIVE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Load lib
# shellcheck disable=SC1090
source "${RELATIVE_DIR}/lib.sh"

# Command implementation
function command::help() {
  echo "-- Help Menu"
  echo "> ./scripts/workflow.sh setup     | Setup the project"
  echo "> ./scripts/workflow.sh generate  | Generate project files"
  echo "> ./scripts/workflow.sh build     | Build the project"
  echo "> ./scripts/workflow.sh test      | Run tests on this project"
  echo "> ./scripts/workflow.sh release   | Prepare project for release"
  echo "> ./scripts/workflow.sh help      | Display this help menu"
}

function command::check() {
  log::action "Checking if needed commands are installs"
  command::is_present "python3.9"
  command::is_present "pip3"
  case "${1}" in
    build)
      command::is_present "gcc"
      ;;
    test)
      ;;
    *)
      echo "Unknown argument: ${arg}"
      ;;
  esac
}

function command::setup() {
  # Constants
  HOOK_DIR=${BASE_PROJECT}/.git/hooks

  # Create directory
  mkdir -p "${HOOK_DIR}"

  # Remove all old hooks before anything
  rm -f "${HOOK_DIR}/commit-msg"
  rm -f "${HOOK_DIR}/pre-commit"
  log::success "remove old hooks"

  # Copy new ones
  cp "${RELATIVE_DIR}/hook-commit-msg.sh" "${HOOK_DIR}/commit-msg"
  cp "${RELATIVE_DIR}/hook-pre-commit.sh" "${HOOK_DIR}/pre-commit"
  log::success "copy new hooks"
}

function command::generate() {
  process::try "generate pyinstaller spec" pyinstaller -n temply \
    --onefile --noconfirm "${BASE_PROJECT}/bin/temply"
}

function command::build() {
  process::try "clean previous build" rm -rf build/ dist/
  process::try "install pip3 dependencies" pip3 install -r requirements.txt -r requirements-build.txt
  process::try "create a binary executable" pyinstaller temply.spec
}

function command::test() {
  process::try "install pip3 dependencies" pip3 install -r requirements.txt -r requirements-tests.txt
  process::try "run tests" tox
}

function command::release() {
  local current_version=$(grep -oP "__version__ = '(.*)'" "temply/__init__.py" | grep -oP "[0-9\.-]+[a-z]*")
  echo "Current version: ${current_version}"
  echo -n "New version: "
  read -r new_version
  sed -i "s/${current_version}/${new_version}/g" "temply/__init__.py"
}

# Parse argument
arg="${1-}"
if [[ -z "${arg}" ]] ; then
  echo "Expected arg to be present"
  command::help
else
  case "${arg}" in
    help)
      command::help
      ;;
    setup)
      command::setup
      ;;
    generate)
      command::generate
      ;;
    build)
      command::check "build"
      command::build
      ;;
    test)
      command::check "test"
      command::test
      ;;
    release)
      command::release
      ;;
    *)
      echo "Unknown argument: ${arg}"
      command::help
      ;;
  esac
fi
