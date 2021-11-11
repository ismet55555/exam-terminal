#!/bin/bash

set -e

# Parsing the script arguments
CURRENT_BRANCH=$1
TARGET_BRANCH=$2
echo "Current branch: $CURRENT_BRANCH"
echo "Target branch: $TARGET_BRANCH"

ONLY_SKIPPED_FILES=True
MD=".md"
echo "Files to ignore: ${MD}"

# Checking the diff between branches
echo "Looking for all changed files compared to target branch ..."
CHANGED_FILES=$(git diff --name-only ${TARGET_BRANCH}...${CURRENT_BRANCH})

# Looping through all changed filespaths
for CHANGED_FILE in $CHANGED_FILES; do
  echo "Changed File: $CHANGED_FILE"
  # Checking if at least one file is not an ingored file
  if ! [[ $CHANGED_FILE =~ $MD ]]; then
    ONLY_SKIPPED_FILES=False
    break
  fi
done

if [[ $ONLY_SKIPPED_FILES == True ]]; then
  echo "Only $MD files have changed. Exiting ..."
  exit 1
else
  echo "No $MD files have changed. Continuing with build ..."
fi

exit 0
