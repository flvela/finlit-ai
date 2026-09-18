#!/usr/bin/env bash

echo "==> flake8"
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics --indent-size=2 --exclude=.venv

echo "==> pylint (src)"
pylint --indent-string='  ' --max-line-length=127 src

echo "==> pylint (tests)"
pylint --indent-string='  ' --max-line-length=127 tests

echo "==> pytest (coverage)"
pytest --cov=src --cov-report html:coverage

echo "==> All checks completed"