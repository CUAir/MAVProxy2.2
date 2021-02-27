#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
git rev-parse HEAD > "$CURRENT_DIR/commit.txt"