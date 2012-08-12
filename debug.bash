#!/bin/bash
PROJECT_DIRECTORY="$(dirname $(readlink -f "$0"))"
export JOBSCHED_CONFIG="$PROJECT_DIRECTORY/jobsched.cfg"
export PYTHONPATH="$PROJECT_DIRECTORY:$PYTHONPATH"
python -m jobsched --conf-dir . --tasks-dir ./tasks
