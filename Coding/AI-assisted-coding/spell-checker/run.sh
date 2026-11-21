#!/usr/bin/env bash
# Usage: ./run.sh [solution|original|coverage]   (default: solution)
#   solution/original: run main.py, then the tests.  coverage: line + branch coverage of the solution.
cd "$(dirname "$0")"
VARIANT="${1:-solution}"
export PYTHONDONTWRITEBYTECODE=1
if [ "$VARIANT" = "coverage" ]; then
  export PYTHONPATH="solution/src"
  python3 -m coverage run --branch --data-file=/tmp/spell-checker.cov \
    --include="solution/src/distance.py,solution/src/checker.py" \
    -m unittest tests/test_distance.py tests/test_checker.py tests/test_solution_only.py
  python3 -m coverage report -m --data-file=/tmp/spell-checker.cov
  rm -f /tmp/spell-checker.cov
  exit
fi
TESTS="tests/test_distance.py tests/test_checker.py"
[ "$VARIANT" = "solution" ] && TESTS="$TESTS tests/test_solution_only.py"
export PYTHONPATH="$VARIANT/src"
python3 "$VARIANT/src/main.py"
python3 -m unittest -v $TESTS
