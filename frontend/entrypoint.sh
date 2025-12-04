#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Runtime Environment Variable Generator
# ============================================================================
# Generates /public/runtime-env.js from schema at container start
# Platform-agnostic: Works on Cloud Run, Docker, and local dev

# ---------- Compute universal deploy revision ----------
# Try platform-specific vars first, fall back to timestamp
REV="${K_REVISION:-}"                      # Cloud Run
REV="${REV:-${VERCEL_GIT_COMMIT_SHA:-}}"   # Vercel
REV="${REV:-${RENDER_GIT_COMMIT:-}}"       # Render
REV="${REV:-${HEROKU_RELEASE_VERSION:-}}"  # Heroku
REV="${REV:-${SOURCE_VERSION:-}}"          # Generic
REV="${REV:-$(date +%s)}"                  # Fallback: Unix timestamp

echo "Generating runtime environment (revision: ${REV})"

# ---------- Build window.__ENV from all client-visible vars ----------
# This approach is schema-less but safe - only includes public vars
json=$(node -e '
  const out = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (k.startsWith("NEXT_PUBLIC_") && typeof v === "string" && v.length > 0) {
      out[k] = v;
    }
  }
  process.stdout.write(JSON.stringify(out));
')

echo "Collected $(echo "$json" | node -e 'const data = JSON.parse(require("fs").readFileSync(0, "utf-8")); console.log(Object.keys(data).length)') public environment variables"

# ---------- Generate /public/runtime-env.js ----------
export RUNTIME_ENV_JSON="$json"
node <<'NODE'
const fs = require('fs');
const path = require('path');

const runtimeJson = process.env.RUNTIME_ENV_JSON || '{}';
const templatePath = path.join(process.cwd(), 'public', 'runtime-env.js.template');
const outputPath = path.join(process.cwd(), 'public', 'runtime-env.js');
const template = fs.readFileSync(templatePath, 'utf8');

fs.writeFileSync(outputPath, template.replace('$_RUNTIME_ENV_JSON', runtimeJson));
NODE

echo "Generated public/runtime-env.js"

# ---------- Export revision for Next.js to use ----------
export RUNTIME_ENV_REV="$REV"

echo "Starting Next.js server..."

# Execute the command passed to this script (e.g., node server.js)
exec "$@"
