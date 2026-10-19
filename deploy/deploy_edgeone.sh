#!/usr/bin/env bash
# EdgeOne Makers CLI deploy for IDEA-05B
# Usage:
#   bash deploy/deploy_edgeone.sh                 # anonymous, china, temporary URL
#   EDGEONE_TOKEN=xxx bash deploy/deploy_edgeone.sh  # logged-in/API token, long-term
#   bash deploy/deploy_edgeone.sh --claim <SID>   # claim anonymous project
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ZIP="$ROOT/deploy/docs_site.zip"
NAME="${EDGEONE_NAME:-idea-05b-smart-pill-box}"

if [[ "${1:-}" == "--claim" ]]; then
  SID="${2:?usage: --claim <SID>}"
  if [[ -n "${EDGEONE_TOKEN:-}" ]]; then
    npx --yes edgeone makers claim --sid "$SID" -t "$EDGEONE_TOKEN" --json
  else
    npx --yes edgeone makers claim --sid "$SID" --json
  fi
  exit 0
fi

if [[ ! -f "$ZIP" ]]; then
  echo "building $ZIP ..."
  python3 - "$ZIP" "$ROOT/IDEA-05_智能药盒_交付包_20261018/docs" <<'PY'
import os, sys, zipfile
out, base = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
    for dp, dn, fn in os.walk(base):
        dn.sort(); fn.sort()
        for f in fn:
            if f == '.DS_Store': continue
            p = os.path.join(dp, f)
            z.write(p, os.path.relpath(p, base))
print('zip', round(os.path.getsize(out)/1024/1024, 2), 'MB')
PY
fi

if [[ -n "${EDGEONE_TOKEN:-}" ]]; then
  echo "deploy with API token -> long-term project"
  npx --yes edgeone makers deploy "$ZIP" -n "$NAME" -t "$EDGEONE_TOKEN" --json
else
  echo "deploy anonymous -> temporary china preview"
  npx --yes edgeone makers deploy "$ZIP" -n "$NAME" --anonymous --site china --json
fi
