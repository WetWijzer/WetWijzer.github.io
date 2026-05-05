#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_FILE="$ROOT/ppd/daemon/ppd-daemon.pid"
CHILD_PID_FILE="$ROOT/ppd/daemon/ppd-daemon.child.pid"
OUT_FILE="$ROOT/ppd/daemon/ppd-daemon.out"
STATUS_FILE="$ROOT/ppd/daemon/status.json"
LIFECYCLE_LOG="$ROOT/ppd/daemon/ppd-daemon-lifecycle.jsonl"
SUPERVISOR_PID_FILE="$ROOT/ppd/daemon/ppd-supervisor.pid"
SUPERVISOR_CHILD_PID_FILE="$ROOT/ppd/daemon/ppd-supervisor.child.pid"
SUPERVISOR_OUT_FILE="$ROOT/ppd/daemon/ppd-supervisor.out"
SUPERVISOR_STATUS_FILE="$ROOT/ppd/daemon/supervisor-status.json"
SUPERVISOR_LIFECYCLE_LOG="$ROOT/ppd/daemon/ppd-supervisor-lifecycle.jsonl"
WATCHDOG_SCRIPT="$ROOT/ppd/daemon/watchdog.sh"
DAEMON_UNIT="ppd-daemon.service"
SUPERVISOR_UNIT="ppd-supervisor.service"
SUPERVISOR_USER_UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SUPERVISOR_USER_UNIT_FILE="$SUPERVISOR_USER_UNIT_DIR/$SUPERVISOR_UNIT"

systemd_available() {
  command -v systemd-run >/dev/null 2>&1 && systemctl --user list-units >/dev/null 2>&1
}

systemd_unit_active() {
  local unit="$1"
  systemctl --user is-active --quiet "$unit" >/dev/null 2>&1
}

supervisor_systemd_enabled() {
  [[ "${PPD_SUPERVISOR_DISABLE_SYSTEMD:-0}" != "1" ]] && systemd_available
}

systemd_unit_loaded() {
  local unit="$1"
  [[ "$(systemctl --user show "$unit" --property=LoadState --value 2>/dev/null || true)" == "loaded" ]]
}

systemd_unit_main_pid() {
  local unit="$1"
  systemctl --user show "$unit" --property=MainPID --value 2>/dev/null || true
}

wait_for_pid_file_process() {
  local pid_file="$1"
  local timeout_seconds="${2:-10}"
  local pid
  local deadline
  deadline=$((SECONDS + timeout_seconds))

  while (( SECONDS < deadline )); do
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1; then
      echo "$pid"
      return 0
    fi
    sleep 0.2
  done

  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1; then
    echo "$pid"
    return 0
  fi
  return 1
}

wait_for_systemd_inactive() {
  local unit="$1"
  local timeout_seconds="${2:-10}"
  local state
  local deadline
  deadline=$((SECONDS + timeout_seconds))

  while (( SECONDS < deadline )); do
    state="$(systemctl --user show "$unit" --property=ActiveState --value 2>/dev/null || true)"
    if [[ "$state" == "inactive" || "$state" == "failed" || -z "$state" ]]; then
      return 0
    fi
    sleep 0.2
  done
  return 1
}

wait_for_systemd_unloaded() {
  local unit="$1"
  local timeout_seconds="${2:-5}"
  local load_state
  local deadline
  deadline=$((SECONDS + timeout_seconds))

  while (( SECONDS < deadline )); do
    load_state="$(systemctl --user show "$unit" --property=LoadState --value 2>/dev/null || true)"
    if [[ "$load_state" == "not-found" || -z "$load_state" ]]; then
      return 0
    fi
    sleep 0.2
  done
  return 1
}

wait_for_systemd_main_pid() {
  local unit="$1"
  local timeout_seconds="${2:-10}"
  local pid
  local state
  local deadline
  deadline=$((SECONDS + timeout_seconds))

  while (( SECONDS < deadline )); do
    pid="$(systemctl --user show "$unit" --property=MainPID --value 2>/dev/null || true)"
    state="$(systemctl --user show "$unit" --property=ActiveState --value 2>/dev/null || true)"
    if [[ "$pid" =~ ^[0-9]+$ ]] && [[ "$pid" != "0" ]] && ps -p "$pid" >/dev/null 2>&1; then
      echo "$pid"
      return 0
    fi
    [[ "$state" == "failed" || "$state" == "inactive" ]] && break
    sleep 0.2
  done
  return 1
}

stop_systemd_unit() {
  local unit="$1"
  if systemd_available; then
    systemctl --user stop "$unit" >/dev/null 2>&1 || true
    wait_for_systemd_inactive "$unit" 10 || true
    systemctl --user reset-failed "$unit" >/dev/null 2>&1 || true
    wait_for_systemd_unloaded "$unit" 5 || true
  fi
}

run_systemd_watchdog_unit() {
  local unit="$1"
  local command="$2"
  local restart_policy="${3:-always}"

  if systemd-run --user --unit="$unit" --collect --property=Restart="$restart_policy" --property=RestartSec=5 --property=KillMode=process --working-directory="$ROOT" \
    bash -lc "$command" >/dev/null; then
    return 0
  fi

  return 1
}

write_supervisor_user_unit() {
  local tmp_file
  mkdir -p "$SUPERVISOR_USER_UNIT_DIR"
  tmp_file="$(mktemp "$SUPERVISOR_USER_UNIT_FILE.tmp.XXXXXX")"
  cat > "$tmp_file" <<EOF
[Unit]
Description=PP&D autonomous supervisor
After=default.target

[Service]
Type=simple
WorkingDirectory=$ROOT
Environment=PYTHONPATH=ipfs_datasets_py
Environment=PPD_LLM_BACKEND=llm_router
Environment=IPFS_DATASETS_PY_CODEX_SANDBOX=read-only
Environment=PPD_SUPERVISOR_HONOR_TERM=1
ExecStartPre=/usr/bin/rm -f $SUPERVISOR_PID_FILE.stop $SUPERVISOR_CHILD_PID_FILE
ExecStart=/usr/bin/bash -lc 'exec python3 ppd/daemon/ppd_supervisor.py --watch --interval 120 --exception-backoff 5 --termination-storm-threshold 8 --termination-storm-backoff 900 --apply --self-heal --restart-daemon --llm-timeout 300 --honor-term >> "$SUPERVISOR_OUT_FILE" 2>&1'
Restart=always
RestartSec=5
StartLimitIntervalSec=0
TimeoutStopSec=20
KillMode=control-group

[Install]
WantedBy=default.target
EOF
  if [[ ! -f "$SUPERVISOR_USER_UNIT_FILE" ]] || ! cmp -s "$tmp_file" "$SUPERVISOR_USER_UNIT_FILE"; then
    mv "$tmp_file" "$SUPERVISOR_USER_UNIT_FILE"
    systemctl --user daemon-reload >/dev/null 2>&1 || true
  else
    rm -f "$tmp_file"
  fi
}

start_persistent_supervisor_unit() {
  write_supervisor_user_unit
  rm -f "$SUPERVISOR_CHILD_PID_FILE" "$SUPERVISOR_PID_FILE.stop"
  systemctl --user reset-failed "$SUPERVISOR_UNIT" >/dev/null 2>&1 || true
  systemctl --user enable "$SUPERVISOR_UNIT" >/dev/null 2>&1 || true
  systemctl --user start "$SUPERVISOR_UNIT"
}

collect_descendant_pids() {
  local parent="$1"
  local child
  while IFS= read -r child; do
    [[ -z "$child" ]] && continue
    echo "$child"
    collect_descendant_pids "$child"
  done < <(pgrep -P "$parent" 2>/dev/null || true)
}

process_group_for_pid() {
  local pid="$1"
  ps -o pgid= -p "$pid" 2>/dev/null | tr -d '[:space:]'
}

process_running() {
  local pid="${1:-}"
  [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1
}

is_descendant_of() {
  local pid="$1"
  local ancestor="$2"
  local parent

  [[ -z "$pid" || -z "$ancestor" ]] && return 1
  while [[ "$pid" =~ ^[0-9]+$ ]] && [[ "$pid" != "1" ]]; do
    [[ "$pid" == "$ancestor" ]] && return 0
    parent="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d '[:space:]')"
    [[ -z "$parent" || "$parent" == "$pid" ]] && break
    pid="$parent"
  done
  return 1
}

is_current_managed_child() {
  local pid="$1"
  local watchdog_pid_file="$2"
  local child_pid_file="$3"
  local watchdog_pid=""
  local child_pid=""

  if [[ -f "$watchdog_pid_file" ]]; then
    watchdog_pid="$(cat "$watchdog_pid_file" 2>/dev/null || true)"
  fi
  if [[ -f "$child_pid_file" ]]; then
    child_pid="$(cat "$child_pid_file" 2>/dev/null || true)"
  fi

  if process_running "$watchdog_pid" && [[ "$pid" == "$child_pid" ]] && is_descendant_of "$pid" "$watchdog_pid"; then
    return 0
  fi
  if process_running "$watchdog_pid" && is_descendant_of "$pid" "$watchdog_pid"; then
    return 0
  fi
  return 1
}

is_systemd_unit_process() {
  local pid="$1"
  local unit="$2"
  local main_pid

  [[ -z "$pid" || -z "$unit" ]] && return 1
  main_pid="$(systemd_unit_main_pid "$unit")"
  if process_running "$main_pid"; then
    [[ "$pid" == "$main_pid" ]] && return 0
    is_descendant_of "$pid" "$main_pid" && return 0
  fi
  return 1
}

terminate_process_family() {
  local root_pid="$1"
  local label="$2"
  local -a family_pids=()
  local -a process_groups=()
  local pid
  local pgid

  if [[ -z "$root_pid" ]] || ! ps -p "$root_pid" >/dev/null 2>&1; then
    echo "$label not running: ${root_pid:-unknown}"
    return 0
  fi

  mapfile -t family_pids < <(
    {
      echo "$root_pid"
      collect_descendant_pids "$root_pid"
    } | awk 'NF && !seen[$0]++'
  )

  for pid in "${family_pids[@]}"; do
    pgid="$(process_group_for_pid "$pid")"
    [[ -n "$pgid" ]] && process_groups+=("$pgid")
  done
  mapfile -t process_groups < <(printf '%s\n' "${process_groups[@]}" | awk 'NF && !seen[$0]++')

  for pgid in "${process_groups[@]}"; do
    kill -TERM -- "-$pgid" 2>/dev/null || true
  done
  sleep 2
  for pgid in "${process_groups[@]}"; do
    kill -KILL -- "-$pgid" 2>/dev/null || true
  done

  echo "$label stopped: $root_pid"
}

sweep_orphaned_ppd_llm_children() {
  local pid
  local daemon_child_pid=""
  if [[ -f "$CHILD_PID_FILE" ]]; then
    daemon_child_pid="$(cat "$CHILD_PID_FILE" 2>/dev/null || true)"
    process_running "$daemon_child_pid" || daemon_child_pid=""
  fi

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    if [[ -z "$daemon_child_pid" ]] || ! is_descendant_of "$pid" "$daemon_child_pid"; then
      terminate_process_family "$pid" "Orphaned PP&D LLM child"
    fi
  done < <(
    ps -eo pid=,ppid=,args= |
      awk '/python3 -c/ && /PPD_LLM_PROMPT_FILE/ && /ipfs_datasets_py/ {print $1}'
  )
}

sweep_unwatched_ppd_daemon_children() {
  local pid
  while read -r pid; do
    [[ -z "$pid" ]] && continue
    if systemd_available && is_systemd_unit_process "$pid" "$DAEMON_UNIT"; then
      continue
    fi
    if ! is_current_managed_child "$pid" "$PID_FILE" "$CHILD_PID_FILE"; then
      terminate_process_family "$pid" "Unwatched PP&D daemon"
    fi
  done < <(
    ps -eo pid=,args= |
      awk '/python3 ppd\/daemon\/ppd_daemon.py --apply --watch/ {print $1}'
  )
}

sweep_unwatched_ppd_supervisor_children() {
  local pid
  while read -r pid; do
    [[ -z "$pid" ]] && continue
    if systemd_available && is_systemd_unit_process "$pid" "$SUPERVISOR_UNIT"; then
      continue
    fi
    if ! is_current_managed_child "$pid" "$SUPERVISOR_PID_FILE" "$SUPERVISOR_CHILD_PID_FILE"; then
      terminate_process_family "$pid" "Unwatched PP&D supervisor"
    fi
  done < <(
    ps -eo pid=,args= |
      awk '/python3 ppd\/daemon\/ppd_supervisor.py --watch/ {print $1}'
  )
}

start() {
  sweep_unwatched_ppd_daemon_children
  sweep_orphaned_ppd_llm_children

  if [[ -f "$PID_FILE" ]]; then
    local old_pid
    old_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && ps -p "$old_pid" >/dev/null 2>&1; then
      echo "PP&D daemon watchdog already running: $old_pid"
      return 0
    fi
    rm -f "$PID_FILE" "$CHILD_PID_FILE" "$PID_FILE.stop"
  fi

  if systemd_available; then
    stop_systemd_unit "$DAEMON_UNIT"
    run_systemd_watchdog_unit "$DAEMON_UNIT" \
      "exec bash '$WATCHDOG_SCRIPT' daemon '$PID_FILE' '$CHILD_PID_FILE' '$LIFECYCLE_LOG' 5 env PYTHONPATH=ipfs_datasets_py PPD_LLM_BACKEND=llm_router IPFS_DATASETS_PY_CODEX_SANDBOX=read-only python3 ppd/daemon/ppd_daemon.py --apply --watch --iterations 0 --interval 0 --llm-timeout 300 --llm-max-new-tokens 1536 --max-prompt-chars 20000 --max-compact-prompt-chars 3600 --crash-backoff 5 --repair-validation-failures >> '$OUT_FILE' 2>&1"
  else
    setsid -f bash -c "cd '$ROOT' && exec bash '$WATCHDOG_SCRIPT' daemon '$PID_FILE' '$CHILD_PID_FILE' '$LIFECYCLE_LOG' 5 env PYTHONPATH=ipfs_datasets_py PPD_LLM_BACKEND=llm_router IPFS_DATASETS_PY_CODEX_SANDBOX=read-only python3 ppd/daemon/ppd_daemon.py --apply --watch --iterations 0 --interval 0 --llm-timeout 300 --llm-max-new-tokens 1536 --max-prompt-chars 20000 --max-compact-prompt-chars 3600 --crash-backoff 5 --repair-validation-failures >> '$OUT_FILE' 2>&1"
  fi
  local pid
  if ! pid="$(wait_for_pid_file_process "$PID_FILE" 10)"; then
    echo "PP&D daemon did not start; see $OUT_FILE" >&2
    if systemd_available; then
      systemctl --user --no-pager --plain status "$DAEMON_UNIT" | sed -n '1,8p' >&2 || true
    fi
    return 1
  fi
  echo "PP&D daemon watchdog started: $pid"
  if [[ -f "$CHILD_PID_FILE" ]]; then
    echo "PP&D daemon child started: $(cat "$CHILD_PID_FILE")"
  fi
}

stop() {
  if [[ ! -f "$PID_FILE" ]]; then
    if [[ -f "$CHILD_PID_FILE" ]]; then
      local child_pid
      child_pid="$(cat "$CHILD_PID_FILE" 2>/dev/null || true)"
      [[ -n "$child_pid" ]] && terminate_process_family "$child_pid" "PP&D daemon child"
      rm -f "$CHILD_PID_FILE" "$PID_FILE.stop"
    fi
    sweep_unwatched_ppd_daemon_children
    sweep_orphaned_ppd_llm_children
    echo "No PID file at $PID_FILE"
    return 0
  fi
  local pid
  pid="$(cat "$PID_FILE")"
  touch "$PID_FILE.stop"
  stop_systemd_unit "$DAEMON_UNIT"
  terminate_process_family "$pid" "PP&D daemon"
  if [[ -f "$CHILD_PID_FILE" ]]; then
    local child_pid
    child_pid="$(cat "$CHILD_PID_FILE" 2>/dev/null || true)"
    [[ -n "$child_pid" ]] && terminate_process_family "$child_pid" "PP&D daemon child"
  fi
  sweep_unwatched_ppd_daemon_children
  sweep_orphaned_ppd_llm_children
  rm -f "$PID_FILE" "$CHILD_PID_FILE" "$PID_FILE.stop"
}

status() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    echo "watchdog:"
    ps -p "$pid" -o pid,ppid,sid,etime,cmd || true
  fi
  if systemd_available && systemd_unit_active "$DAEMON_UNIT"; then
    echo "systemd:"
    systemctl --user --no-pager --plain status "$DAEMON_UNIT" | sed -n '1,8p' || true
  fi
  if [[ -f "$CHILD_PID_FILE" ]]; then
    local child_pid
    child_pid="$(cat "$CHILD_PID_FILE")"
    echo "child:"
    ps -p "$child_pid" -o pid,ppid,sid,etime,cmd || true
  fi
  if [[ -f "$STATUS_FILE" ]]; then
    cat "$STATUS_FILE"
  fi
  if [[ -f "$LIFECYCLE_LOG" ]]; then
    echo
    echo "recent lifecycle:"
    tail -n 5 "$LIFECYCLE_LOG"
  fi
}

supervisor_start() {
  sweep_unwatched_ppd_supervisor_children

  if [[ -f "$SUPERVISOR_PID_FILE" ]]; then
    local old_pid
    old_pid="$(cat "$SUPERVISOR_PID_FILE" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && ps -p "$old_pid" >/dev/null 2>&1; then
      echo "PP&D supervisor watchdog already running: $old_pid"
      return 0
    fi
    rm -f "$SUPERVISOR_PID_FILE" "$SUPERVISOR_CHILD_PID_FILE" "$SUPERVISOR_PID_FILE.stop"
  fi

  if supervisor_systemd_enabled; then
    start_persistent_supervisor_unit
    local pid
    if ! pid="$(wait_for_systemd_main_pid "$SUPERVISOR_UNIT" 10)"; then
      echo "PP&D supervisor did not start; see $SUPERVISOR_OUT_FILE" >&2
      systemctl --user --no-pager --plain status "$SUPERVISOR_UNIT" | sed -n '1,8p' >&2 || true
      return 1
    fi
    echo "$pid" > "$SUPERVISOR_PID_FILE"
  else
    if systemd_available; then
      stop_systemd_unit "$SUPERVISOR_UNIT"
    fi
    setsid -f bash -c "cd '$ROOT'; rm -f '$SUPERVISOR_PID_FILE.stop' '$SUPERVISOR_CHILD_PID_FILE'; echo \$\$ > '$SUPERVISOR_PID_FILE'; exec env PYTHONPATH=ipfs_datasets_py PPD_LLM_BACKEND=llm_router IPFS_DATASETS_PY_CODEX_SANDBOX=read-only python3 ppd/daemon/ppd_supervisor.py --watch --interval 120 --exception-backoff 5 --termination-storm-threshold 8 --termination-storm-backoff 900 --apply --self-heal --restart-daemon --llm-timeout 300 >> '$SUPERVISOR_OUT_FILE' 2>&1"
    local pid
    if ! pid="$(wait_for_pid_file_process "$SUPERVISOR_PID_FILE" 10)"; then
      echo "PP&D supervisor did not start; see $SUPERVISOR_OUT_FILE" >&2
      return 1
    fi
  fi
  echo "PP&D supervisor started: $pid"
  if [[ -f "$SUPERVISOR_CHILD_PID_FILE" ]]; then
    echo "PP&D supervisor child started: $(cat "$SUPERVISOR_CHILD_PID_FILE")"
  fi
}

supervisor_stop() {
  touch "$SUPERVISOR_PID_FILE.stop"
  if systemd_available; then
    stop_systemd_unit "$SUPERVISOR_UNIT"
  fi
  if [[ ! -f "$SUPERVISOR_PID_FILE" ]]; then
    if [[ -f "$SUPERVISOR_CHILD_PID_FILE" ]]; then
      local child_pid
      child_pid="$(cat "$SUPERVISOR_CHILD_PID_FILE" 2>/dev/null || true)"
      [[ -n "$child_pid" ]] && terminate_process_family "$child_pid" "PP&D supervisor child"
      rm -f "$SUPERVISOR_CHILD_PID_FILE" "$SUPERVISOR_PID_FILE.stop"
    fi
    sweep_unwatched_ppd_supervisor_children
    echo "No supervisor PID file at $SUPERVISOR_PID_FILE"
    return 0
  fi
  local pid
  pid="$(cat "$SUPERVISOR_PID_FILE")"
  terminate_process_family "$pid" "PP&D supervisor"
  if [[ -f "$SUPERVISOR_CHILD_PID_FILE" ]]; then
    local child_pid
    child_pid="$(cat "$SUPERVISOR_CHILD_PID_FILE" 2>/dev/null || true)"
    [[ -n "$child_pid" ]] && terminate_process_family "$child_pid" "PP&D supervisor child"
  fi
  sweep_unwatched_ppd_supervisor_children
  rm -f "$SUPERVISOR_PID_FILE" "$SUPERVISOR_CHILD_PID_FILE" "$SUPERVISOR_PID_FILE.stop"
}

supervisor_status() {
  if systemd_available && systemd_unit_active "$SUPERVISOR_UNIT"; then
    local main_pid
    main_pid="$(systemd_unit_main_pid "$SUPERVISOR_UNIT")"
    if process_running "$main_pid"; then
      echo "$main_pid" > "$SUPERVISOR_PID_FILE"
      echo "supervisor:"
      ps -p "$main_pid" -o pid,ppid,sid,etime,cmd || true
    fi
    echo "systemd:"
    systemctl --user --no-pager --plain status "$SUPERVISOR_UNIT" | sed -n '1,8p' || true
  elif [[ -f "$SUPERVISOR_PID_FILE" ]]; then
    local pid
    pid="$(cat "$SUPERVISOR_PID_FILE")"
    echo "supervisor:"
    ps -p "$pid" -o pid,ppid,sid,etime,cmd || true
  fi
  if [[ -f "$SUPERVISOR_CHILD_PID_FILE" ]]; then
    local child_pid
    child_pid="$(cat "$SUPERVISOR_CHILD_PID_FILE")"
    echo "child:"
    ps -p "$child_pid" -o pid,ppid,sid,etime,cmd || true
  fi
  if [[ -f "$SUPERVISOR_STATUS_FILE" ]]; then
    cat "$SUPERVISOR_STATUS_FILE"
  fi
  if [[ -f "$SUPERVISOR_LIFECYCLE_LOG" ]]; then
    echo
    echo "recent lifecycle:"
    tail -n 5 "$SUPERVISOR_LIFECYCLE_LOG"
  fi
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  logs) tail -f "$OUT_FILE" ;;
  doctor) python3 "$ROOT/ppd/daemon/ppd_supervisor.py" --once --apply --self-heal --restart-daemon --llm-timeout 300 ;;
  supervisor-start) supervisor_start ;;
  supervisor-stop) supervisor_stop ;;
  supervisor-restart) supervisor_stop; supervisor_start ;;
  supervisor-status) supervisor_status ;;
  supervisor-logs) tail -f "$SUPERVISOR_OUT_FILE" ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs|doctor|supervisor-start|supervisor-stop|supervisor-restart|supervisor-status|supervisor-logs}" >&2
    exit 2
    ;;
esac
