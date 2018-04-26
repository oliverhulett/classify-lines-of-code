# shellcheck shell=bash
##
##	This file is intended to be sourced.  It will setup a development environment for this project.
##	Once this file "returns" you will be in a python virtual environment with this project installed
##	in develop mode and all the testing and development dependencies installed.
##

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VENV_DIR="${HERE}/.venv"

# Requirements for the development environment and testing only.  Runtime dependencies should be listed in setup.py.
read -r -d '' REQUIREMENTS <<-'EOF'
	invoke
	unittest2
	coverage
EOF

if [ ! -e "${VENV_DIR}/bin/activate" ]; then
	virtualenv -p "$(command which python2.7)" --prompt="(.venv:cloc) " "${VENV_DIR}" || return 1
fi

# shellcheck source=.venv/bin/activate
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [ ! -e "${VENV_DIR}/requirements.txt" ] || [ "$(command cat "${VENV_DIR}/requirements.txt")" != "${REQUIREMENTS}" ]; then
	echo "${REQUIREMENTS}" >"${VENV_DIR}/requirements.txt"
	pip install -q -r "${VENV_DIR}/requirements.txt"
	pip uninstall -q --yes cloc
	pip install -q -e "${HERE}"
fi
