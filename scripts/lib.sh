#!/usr/bin/env bash

# Strict mode
set -euo pipefail
trap 's=$?; echo >&2 "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR

# Found current script directory
readonly RELATIVE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Found project directory
readonly BASE_PROJECT="$(dirname "${RELATIVE_DIR}")"

########################################
# Log an actions.
# Arguments:
#   Any texts.
# Outputs:
#   Log a message as action.
########################################
function log::action() {
  echo -e "\033[33m⇒\033[0m $@"
}

########################################
# Log a failure.
# Arguments:
#   Any texts.
# Outputs:
#   Log a message as failure.
########################################
function log::failure() {
  echo -e "\033[31m✗\033[0m Failed to $@"
}

########################################
# Log a success.
# Arguments:
#   Any texts.
# Outputs:
#   Log a message as success.
########################################
function log::success() {
  echo -e "\033[32m✓\033[0m Succeeded to $@"
}

########################################
# Check if a command is present in the current context.
# Arguments:
#   Command to check.
# Returns:
#   0 if the command is present.
#   1 otherwise.
########################################
function command::is_present() {
  if ! [ -x "$(command -v "${1}")" ]; then
    log::failure "locate command '${1}'" >&2
    exit 1
  fi
}

########################################
# Try to run a command with arguments.
# Arguments:
#   Any arguments.
# Returns:
#   Exit status of the command executed.
########################################
function process::try() {
  ${@:2}
  status="$?"
  if [ "$status" -eq 0 ]; then
    log::success "${1}"
  else
    log::failure "${1}"
    exit "$status"
  fi
}

########################################
# Try to run a command quietly with arguments.
# Arguments:
#   Any arguments.
# Returns:
#   Exit status of the command executed.
########################################
function process::try_quiet() {
  ${@:2} > /dev/null
  local status="$?"
  if [ "${status}" -eq 0 ]; then
    log::success "${1}"
  else
    log::failure "${1}"
    exit "${status}"
  fi
}

########################################
# Retrive an environment variable.
# Arguments:
#   None.
# Outputs:
#   Environment variable value.
# Returns:
#   0 if the environment variable is present.
#   1 otherwise.
########################################
function env::get() {
  local var=$(printf '%s\n' "${!1}")
  if [ -z "${var}" ]; then
    log::failure "retrieve environment '${1}' variable"
    exit 1
  fi
  echo -e "${var}"
}

########################################
# Retrive an environment variable or return default value.
# Arguments:
#   None.
# Outputs:
#   Environment variable value or default value.
########################################
function env::get_or_default() {
  local var=$(printf '%s\n' "${!1}")
  if [ -z "${var}" ]; then
    echo -e "${2}"
  else
    echo -e "${var}"
  fi
}

########################################
# Retrive an environment variable or return readed value.
# Arguments:
#   None.
# Outputs:
#   Environment variable value or readed value.
########################################
function env::get_or_read() {
  local var=$(printf '%s\n' "${!1}")
  if [ -z "${var}" ]; then
    read -p "Value for ${1}: `echo $'\n> '`" var
  fi
  echo -e "${var}"
}

log::action "The script you are running has basename $(basename "$0"), dirname $(dirname "$0")"
log::action "The present working directory is $(pwd)"
