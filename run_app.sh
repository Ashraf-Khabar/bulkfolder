#! /bin/sh

set -x

BASE_PATH="./src"
BASE_MODULE_RUN="bulkfolder.ui.main"

pip install -r requirements.txt

cd ${BASE_PATH}
python -m ${BASE_MODULE_RUN}