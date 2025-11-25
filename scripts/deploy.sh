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

"${SSH_CMD[@]}" bash -s <<EOF
set -euo pipefail
echo "Pulling image: $IMAGE"
docker pull "$IMAGE" || echo "docker pull failed, continuing"
if [ -f "$REMOTE_COMPOSE_PATH" ]; then
  echo "Found compose at $REMOTE_COMPOSE_PATH — pulling and restarting services"
  docker-compose -f "$REMOTE_COMPOSE_PATH" pull || true
  docker-compose -f "$REMOTE_COMPOSE_PATH" up -d || true
else
  echo "Compose file not found at $REMOTE_COMPOSE_PATH — running container directly"
  docker run -d --name youchoo --restart unless-stopped -p 8000:8000 "$IMAGE" || true
fi
EOF

if [[ -n "$TMP_KEY" ]]; then
  rm -f "$TMP_KEY"
fi

echo "Deployment triggered: $IMAGE on $DEPLOY_HOST"
