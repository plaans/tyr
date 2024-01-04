#!/bin/bash
# Update the version in `pyproject.toml` and the date in `LICENSE.md`.
# Usage: ./release.sh <VERSION> <DATE>

set -e;
cd "${0%/*}" || exit 1;   # Go to the script location
cd .. || exit 1;          # Go to the base directory
version=$1;
date=$2;

# Update version in `pyproject.toml`
sed -ri 's/version = \"[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z]+\.[0-9]+)?\"/version = \"'$version'\"/' pyproject.toml;

# Update date in `LICENSE.md`
sdate=$(date --date='@'$((date/1000)) --rfc-3339=date);
sed -ri 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/'$sdate'/' LICENSE.md;
