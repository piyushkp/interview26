#!/usr/bin/env bash
# Usage: ./run.sh [solution|original|coverage]   (default: solution)
#   solution/original: run main.py, then the tests.  coverage: line + branch coverage of the solution.
cd "$(dirname "$0")"
VARIANT="${1:-solution}"
export PYTHONDONTWRITEBYTECODE=1
if [ "$VARIANT" = "coverage" ]; then
  export PYTHONPATH="solution/src"
  python3 -m coverage run --branch --data-file=/tmp/max-unique-char.cov \
    --include="solution/src/word_list.py,solution/src/solver.py" \
    -m unittest tests/test_word_list.py tests/test_solver.py tests/test_solution_only.py
  python3 -m coverage report -m --data-file=/tmp/max-unique-char.cov
  rm -f /tmp/max-unique-char.cov
  exit
fi
TESTS="tests/test_word_list.py tests/test_solver.py"
[ "$VARIANT" = "solution" ] && TESTS="$TESTS tests/test_solution_only.py"
export PYTHONPATH="$VARIANT/src"
python3 "$VARIANT/src/main.py"
python3 -m unittest -v $TESTS
