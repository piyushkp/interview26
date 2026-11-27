#!/usr/bin/env bash
# Usage: ./run.sh [solution|origin|coverage]   (default: solution)
#   solution/original: run main.py, then the tests.  coverage: line + branch coverage of the solution.
cd "$(dirname "$0")"
VARIANT="${1:-solution}"
export PYTHONDONTWRITEBYTECODE=1
if [ "$VARIANT" = "coverage" ]; then
  export PYTHONPATH="solution/src:tests"
  python3 -m coverage run --branch --data-file=/tmp/task-scheduler.cov \
    --include="solution/src/scheduler.py,solution/src/optimizer.py" \
    -m unittest tests/test_scheduler.py tests/test_optimizer.py tests/test_solution_only.py
  python3 -m coverage report -m --data-file=/tmp/task-scheduler.cov
  rm -f /tmp/task-scheduler.cov
  exit
fi
TESTS="tests/test_scheduler.py tests/test_optimizer.py"
[ "$VARIANT" = "solution" ] && TESTS="$TESTS tests/test_solution_only.py"
export PYTHONPATH="$VARIANT/src:tests"
python3 "$VARIANT/src/main.py"
python3 -m unittest -v $TESTS
