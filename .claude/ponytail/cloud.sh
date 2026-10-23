#!/bin/sh
# Runs a vendored ponytail hook in cloud sessions only. Locally the ponytail plugin runs its own copy.
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
config_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
# Cloud containers start fresh, so mark the status line offer as seen instead of repeating it every session.
mkdir -p "$config_dir" && touch "$config_dir/.ponytail-statusline-nudged"
exec node "$(dirname "$0")/hooks/ponytail-$1.js"
