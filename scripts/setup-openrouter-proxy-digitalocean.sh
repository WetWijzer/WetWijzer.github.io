#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  OPENROUTER_API_KEY=sk-or-... sudo -E bash scripts/setup-openrouter-proxy-digitalocean.sh

Optional environment variables:
  OPENROUTER_PROXY_PORT=8787
  OPENROUTER_PROXY_HOST=127.0.0.1
  OPENROUTER_PROXY_ALLOWED_ORIGINS=https://portland-laws.github.io,http://localhost:5173
  OPENROUTER_PROXY_PUBLIC_IP=178.128.128.216
  OPENROUTER_PROXY_PUBLIC_ORIGIN=https://animegf.chat
  OPENROUTER_PROXY_OPEN_FIREWALL=1
  OPENROUTER_SITE_URL=https://portland-laws.github.io
  OPENROUTER_SITE_NAME="Portland Laws"
  SERVICE_NAME=portland-openrouter-proxy

After setup, point the frontend at:
  VITE_OPENROUTER_BASE_URL=https://animegf.chat:8787/api/openrouter

For GitHub Pages, the proxy URL must be HTTPS. If you use port 8787
from the browser, terminate TLS on that port. Otherwise put Caddy/Nginx
on 443 and use:
  VITE_OPENROUTER_BASE_URL=https://animegf.chat/api/openrouter
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root, for example: sudo -E bash scripts/setup-openrouter-proxy-digitalocean.sh" >&2
  exit 1
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is required." >&2
  echo "Example: OPENROUTER_API_KEY=sk-or-... sudo -E bash scripts/setup-openrouter-proxy-digitalocean.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"
SERVICE_NAME="${SERVICE_NAME:-portland-openrouter-proxy}"
SERVICE_USER="${SUDO_USER:-${USER:-root}}"
SERVICE_GROUP="$(id -gn "${SERVICE_USER}" 2>/dev/null || echo "${SERVICE_USER}")"
PORT="${OPENROUTER_PROXY_PORT:-8787}"
HOST="${OPENROUTER_PROXY_HOST:-127.0.0.1}"
PUBLIC_IP="${OPENROUTER_PROXY_PUBLIC_IP:-}"
PUBLIC_ORIGIN="${OPENROUTER_PROXY_PUBLIC_ORIGIN:-https://animegf.chat}"
ENV_FILE="/etc/${SERVICE_NAME}.env"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ -z "${PUBLIC_IP}" ]]; then
  PUBLIC_IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="src") {print $(i+1); exit}}')"
fi

DEFAULT_ALLOWED_ORIGINS="https://portland-laws.github.io,http://localhost:5173,http://127.0.0.1:5173"
if [[ -n "${PUBLIC_ORIGIN}" ]]; then
  DEFAULT_ALLOWED_ORIGINS+=",${PUBLIC_ORIGIN}"
fi
if [[ -n "${PUBLIC_IP}" ]]; then
  DEFAULT_ALLOWED_ORIGINS+=",http://${PUBLIC_IP}:${PORT}"
fi
ALLOWED_ORIGINS="${OPENROUTER_PROXY_ALLOWED_ORIGINS:-${DEFAULT_ALLOWED_ORIGINS}}"

if ! command -v node >/dev/null 2>&1; then
  echo "Installing Node.js from the Ubuntu/Debian package repositories..."
  apt-get update
  apt-get install -y nodejs npm
fi

NODE_MAJOR="$(node -p "Number(process.versions.node.split('.')[0])")"
if [[ "${NODE_MAJOR}" -lt 18 ]]; then
  echo "Node.js 18+ is required for built-in fetch. Current version: $(node --version)" >&2
  echo "Install Node.js 20 LTS, then rerun this script." >&2
  exit 1
fi

echo "Installing npm dependencies in ${REPO_DIR}..."
cd "${REPO_DIR}"
# The proxy does not use optional native packages such as onnxruntime-node,
# so skip them to avoid network fetches on constrained hosts.
npm ci --omit=dev --omit=optional

if command -v ufw >/dev/null 2>&1 && [[ "${OPENROUTER_PROXY_OPEN_FIREWALL:-1}" == "1" ]]; then
  echo "Opening TCP port ${PORT} in UFW..."
  ufw allow "${PORT}/tcp" || true
fi

echo "Writing ${ENV_FILE}..."
cat > "${ENV_FILE}" <<EOF
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
OPENROUTER_PROXY_PORT=${PORT}
OPENROUTER_PROXY_HOST=${HOST}
OPENROUTER_PROXY_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
OPENROUTER_SITE_URL=${OPENROUTER_SITE_URL:-https://portland-laws.github.io}
OPENROUTER_SITE_NAME=${OPENROUTER_SITE_NAME:-Portland Laws}
EOF
chmod 600 "${ENV_FILE}"
chown root:root "${ENV_FILE}"

echo "Writing ${SERVICE_FILE}..."
cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Portland Laws OpenRouter proxy
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${REPO_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=$(command -v node) ${REPO_DIR}/scripts/openrouter-proxy-server.mjs
Restart=always
RestartSec=3
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=false

[Install]
WantedBy=multi-user.target
EOF

chmod +x "${REPO_DIR}/scripts/openrouter-proxy-server.mjs"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}"

echo
echo "Service status:"
systemctl --no-pager --full status "${SERVICE_NAME}" || true

echo
echo "Health check:"
curl -fsS "http://127.0.0.1:${PORT}/health" || true
echo

cat <<EOF

OpenRouter proxy setup complete.

Local endpoint:
  http://127.0.0.1:${PORT}/api/openrouter/chat/completions

Public endpoint (HTTP):
  http://${PUBLIC_IP:-<your-server-ip>}:${PORT}/api/openrouter/chat/completions

Frontend base URL value:
  VITE_OPENROUTER_BASE_URL=https://animegf.chat:${PORT}/api/openrouter

GitHub Pages is HTTPS, so this URL must also be HTTPS. The Node service
started by this script is plain HTTP. For a direct `:8787` browser URL,
terminate TLS on port ${PORT} and reverse proxy to http://${HOST}:${PORT}.
If OpenVPN owns 443, do not move the proxy there.

Useful commands:
  sudo systemctl status ${SERVICE_NAME}
  sudo journalctl -u ${SERVICE_NAME} -f
  sudo systemctl restart ${SERVICE_NAME}

Quick POST smoke test:
  curl -sS http://127.0.0.1:${PORT}/api/openrouter/chat/completions \\
    -H 'Content-Type: application/json' \\
    -d '{"model":"liquid/lfm-2.5-1.2b-instruct:free","messages":[{"role":"user","content":"Say ok."}],"max_tokens":8}'
EOF
