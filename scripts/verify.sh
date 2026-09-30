#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://localhost:3000/api/health >/dev/null
curl -fsS http://localhost:8001/health >/dev/null

echo "ImpactTrace scaffold health checks passed."
