#!/usr/bin/env bash
set -euo pipefail

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
cp "$(dirname "$0")/update_iti_trades.mjs" "$work_dir/update_iti_trades.mjs"
ln -s /home/angsuman/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules "$work_dir/node_modules"
/home/angsuman/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node "$work_dir/update_iti_trades.mjs"
