#!/usr/bin/env bash
set -euo pipefail

# Manage podman-compose up/down/status for chatbot and langfuse
# Usage:
#   ./manage_podman_compose.sh status                # show status for both
#   ./manage_podman_compose.sh status chatbot        # show status for chatbot only
#   ./manage_podman_compose.sh up chatbot            # podman-compose up chatbot
#   ./manage_podman_compose.sh up langfuse           # podman-compose up langfuse
#   ./manage_podman_compose.sh up both               # podman-compose up both
#   ./manage_podman_compose.sh down langfuse         # podman-compose down langfuse
# Notes:
# - Script expects `podman-compose` to be installed and available in PATH.
# - Compose files are expected in the repository root:
#     chatbot-compose.yml and langfuse-compose.yml

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

declare -A COMPOSE_FILE
declare -A PROJECT_NAME

COMPOSE_FILE[chatbot]="$ROOT_DIR/chatbot-compose.yml"
PROJECT_NAME[chatbot]="chatbot"

COMPOSE_FILE[langfuse]="$ROOT_DIR/langfuse-compose.yml"
PROJECT_NAME[langfuse]="langfuse"

print_help(){
  sed -n '1,120p' "$0" | sed -n '1,40p'
}

ensure_podman_compose(){
  if ! command -v podman-compose >/dev/null 2>&1; then
    echo "Error: podman-compose not found in PATH. Please install it or adjust the script to use 'podman compose'." >&2
    exit 2
  fi
}

project_has_running(){
  local proj="$1"
  # Consider a compose "up" if any running container name begins with the project name
  podman ps --format '{{.Names}}' | grep -E "^${proj}" >/dev/null 2>&1
}

status_one(){
  local key="$1"
  local proj="${PROJECT_NAME[$key]}"
  if project_has_running "$proj"; then
    echo "$key: UP"
  else
    echo "$key: DOWN"
  fi
}

status_all(){
  for k in "${!COMPOSE_FILE[@]}"; do
    status_one "$k"
  done
}

run_compose_up(){
  local key
  for key in "$@"; do
    local file="${COMPOSE_FILE[$key]}"
    local proj="${PROJECT_NAME[$key]}"
    if [ ! -f "$file" ]; then
      echo "Skipping $key: compose file not found: $file" >&2
      continue
    fi
    echo "Bringing up $key (file: $file, project: $proj) ..."
    podman-compose -f "$file" -p "$proj" up -d || echo "podman-compose up failed for $key" >&2
  done
}

run_compose_down(){
  local key
  for key in "$@"; do
    local file="${COMPOSE_FILE[$key]}"
    local proj="${PROJECT_NAME[$key]}"
    if [ ! -f "$file" ]; then
      echo "Skipping $key: compose file not found: $file" >&2
      continue
    fi
    echo "Tearing down $key (file: $file, project: $proj) ..."
    podman-compose -f "$file" -p "$proj" down || echo "podman-compose down failed for $key" >&2
  done
}

if [ $# -lt 1 ]; then
  echo "Usage: $0 {status|up|down} [chatbot|langfuse|both]" >&2
  exit 1
fi

ACTION="$1"
TARGET="${2:-both}"

case "$TARGET" in
  chatbot|langfuse)
    TARGETS=("$TARGET")
    ;;
  both|all)
    TARGETS=(chatbot langfuse)
    ;;
  *)
    echo "Unknown target: $TARGET" >&2
    echo "Valid targets: chatbot, langfuse, both" >&2
    exit 1
    ;;
esac

case "$ACTION" in
  status)
    if [ "${#TARGETS[@]}" -eq 0 ]; then
      status_all
    else
      for t in "${TARGETS[@]}"; do status_one "$t"; done
    fi
    ;;
  up)
    ensure_podman_compose
    run_compose_up "${TARGETS[@]}"
    ;; 
  down)
    ensure_podman_compose
    run_compose_down "${TARGETS[@]}"
    ;;
  help|-h|--help)
    print_help
    ;;
  *)
    echo "Unknown action: $ACTION" >&2
    echo "Valid actions: status, up, down" >&2
    exit 1
    ;;
esac

echo "Done. Current status:"
status_all
