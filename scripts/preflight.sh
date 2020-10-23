#!/bin/bash

set -e

CURRENT_BRANCH=$1

# CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

TARGET_BRANCH='master'
echo "Target branch: $TARGET_BRANCH"

ONLY_SKIPPED_FILES=True
MD=".md"
echo "Files to ignore: ${MD}"

echo "Looking for all changed files compared to target branch ..."
CHANGED_FILES=$(git diff --name-only ${TARGET_BRANCH}...${CURRENT_BRANCH})

echo "$CHANGED_FILES"

for CHANGED_FILE in $CHANGED_FILES; do
  echo "Changed File: $CHANGED_FILE"
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