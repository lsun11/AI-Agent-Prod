#!/bin/bash
set -euo pipefail

# --- 0. Config ---
APP_NAME="AI-Agent"
VERSION="0.1.0"
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
RELEASE_ROOT="${PROJECT_ROOT}/dist_release"
RELEASE_DIR="${RELEASE_ROOT}/${APP_NAME}-macOS-arm64-v${VERSION}"
ZIP_NAME="${APP_NAME}-macOS-arm64-v${VERSION}.zip"

echo "==> Building release ${ZIP_NAME}"

# --- 1. Clean old build artifacts ---
rm -rf "${DIST_DIR}"
rm -rf "${RELEASE_ROOT}"
mkdir -p "${RELEASE_DIR}"

# --- 2. Run PyInstaller (from your chosen env, e.g. conda 'advanced-agent') ---
cd "${PROJECT_ROOT}"

pyinstaller \
  --name "${APP_NAME}" \
  --onedir \
  --windowed \
  --add-data "static:static" \
  --add-data "static_build:static_build" \
  --add-data "src/saving/fonts:src/saving/fonts" \
  run_local_app.py

# After this, we have: dist/AI-Agent/AI-Agent (+ _internal, etc.)

# --- 3. Copy built app folder into release dir ---
cp -R "${DIST_DIR}/${APP_NAME}" "${RELEASE_DIR}/"

# --- 4. Copy launcher script ---
cp "${PROJECT_ROOT}/Start_Agent.command" "${RELEASE_DIR}/${APP_NAME}"
chmod +x "${RELEASE_DIR}/${APP_NAME}/Start_Agent.command"


# --- 5. Optional: provide env template ---
if [ -f "${PROJECT_ROOT}/.env" ]; then
  cp "${PROJECT_ROOT}/.env" "${RELEASE_DIR}/${APP_NAME}/.env"
fi

# --- 6. Create zip archive ---
cd "${RELEASE_ROOT}"
echo "==> Creating zip archive ${ZIP_NAME}..."
zip -r "${ZIP_NAME}" "$(basename "${RELEASE_DIR}")"

echo "==> Done!"
echo "Release created at: ${RELEASE_ROOT}/${ZIP_NAME}"
