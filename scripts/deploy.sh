#!/usr/bin/env bash
set -euo pipefail

# Simple deployment script to pull a built image on a remote host and restart docker-compose.
# Usage example (locally):
# IMAGE=ghcr.io/OWNER/youchoo:latest DEPLOY_USER=ubuntu DEPLOY_HOST=example.com REMOTE_COMPOSE_PATH=/home/ubuntu/youchoo/docker-compose.yml ./scripts/deploy.sh
# In CI, set these as secrets and call the script via a step that runs on a runner with ssh key injected.

IMAGE="${IMAGE:-}"
DEPLOY_USER="${DEPLOY_USER:-}"
DEPLOY_HOST="${DEPLOY_HOST:-}"
REMOTE_COMPOSE_PATH="${REMOTE_COMPOSE_PATH:-/home/${DEPLOY_USER}/youchoo/docker-compose.yml}"
SSH_KEY="${SSH_KEY:-}"

if [[ -z "$IMAGE" || -z "$DEPLOY_USER" || -z "$DEPLOY_HOST" ]]; then
  echo "Error: require IMAGE, DEPLOY_USER, DEPLOY_HOST environment variables"
  echo "Example: IMAGE=ghcr.io/OWNER/youchoo:latest DEPLOY_USER=ubuntu DEPLOY_HOST=1.2.3.4 ./scripts/deploy.sh"
  exit 1
fi

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes"
TMP_KEY=""

if [[ -n "$SSH_KEY" ]]; then
  TMP_KEY=$(mktemp)
  echo "$SSH_KEY" > "$TMP_KEY"
  chmod 600 "$TMP_KEY"
  SSH_CMD=(ssh -i "$TMP_KEY" $SSH_OPTS "${DEPLOY_USER}@${DEPLOY_HOST}")
else
  SSH_CMD=(ssh $SSH_OPTS "${DEPLOY_USER}@${DEPLOY_HOST}")
fi

echo "Triggering deployment of image: $IMAGE to ${DEPLOY_USER}@${DEPLOY_HOST}"

"${SSH_CMD[@]}" bash -s <<'EOF'
set -euo pipefail
echo "Pulling image: $IMAGE"
docker pull "$IMAGE" || echo "docker pull failed, continuing"

# If MODEL_URL was passed through the environment, export it so docker-compose can use it
if [ -n "${MODEL_URL:-}" ]; then
  echo "Using MODEL_URL: ${MODEL_URL}"
  export MODEL_URL="${MODEL_URL}"
fi

if [ -n "$REMOTE_COMPOSE_PATH" ] && [ -f "$REMOTE_COMPOSE_PATH" ]; then
  echo "Found compose at $REMOTE_COMPOSE_PATH — pulling and restarting services"
  # Pass MODEL_URL via environment when calling docker-compose
  if [ -n "${MODEL_URL:-}" ]; then
    MODEL_URL="$MODEL_URL" docker-compose -f "$REMOTE_COMPOSE_PATH" pull || true
    MODEL_URL="$MODEL_URL" docker-compose -f "$REMOTE_COMPOSE_PATH" up -d || true
  else
    docker-compose -f "$REMOTE_COMPOSE_PATH" pull || true
    docker-compose -f "$REMOTE_COMPOSE_PATH" up -d || true
  fi
else
  echo "Compose file not found at $REMOTE_COMPOSE_PATH — running container directly"
  if [ -n "${MODEL_URL:-}" ]; then
    docker run -d --name youchoo --restart unless-stopped -p 8000:8000 -e MODEL_URL="$MODEL_URL" "$IMAGE" || true
  else
    docker run -d --name youchoo --restart unless-stopped -p 8000:8000 "$IMAGE" || true
  fi
fi
EOF

if [[ -n "$TMP_KEY" ]]; then
  rm -f "$TMP_KEY"
fi

echo "Deployment triggered: $IMAGE on $DEPLOY_HOST"
