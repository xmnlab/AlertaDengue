#!/usr/bin/env bash
current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${current_dir}; cd ..
pytest AlertaDengue/${1}
