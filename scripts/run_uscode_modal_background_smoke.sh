#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${1:-uscode-modal-bg-$(date -u +%Y%m%dT%H%M%SZ)}"
LOG="$ROOT/workspace/test-logs/${RUN_ID}.supervisor.nohup.log"
EXTRA_CODEX_ARGS=(
  --codex-bundle-mode "${USCODE_MODAL_CODEX_BUNDLE_MODE:-vector}"
  --codex-vector-min-similarity "${USCODE_MODAL_CODEX_VECTOR_MIN_SIMILARITY:-0.72}"
  --codex-task-embeddings-provider "${USCODE_MODAL_CODEX_TASK_EMBEDDINGS_PROVIDER:-local_adapter}"
  --codex-task-embeddings-batch-size "${USCODE_MODAL_CODEX_TASK_EMBEDDINGS_BATCH_SIZE:-32}"
  --codex-vector-fallback-mode "${USCODE_MODAL_CODEX_VECTOR_FALLBACK_MODE:-hash}"
  --codex-merge-repair-mode "${USCODE_MODAL_CODEX_MERGE_REPAIR_MODE:-apply_3way}"
  --codex-merge-repair-attempts "${USCODE_MODAL_CODEX_MERGE_REPAIR_ATTEMPTS:-1}"
)
if [[ -n "${USCODE_MODAL_CODEX_TASK_EMBEDDINGS_MODEL:-}" ]]; then
  EXTRA_CODEX_ARGS+=(--codex-task-embeddings-model "$USCODE_MODAL_CODEX_TASK_EMBEDDINGS_MODEL")
fi
if [[ -n "${USCODE_MODAL_CODEX_TASK_EMBEDDINGS_DEVICE:-}" ]]; then
  EXTRA_CODEX_ARGS+=(--codex-task-embeddings-device "$USCODE_MODAL_CODEX_TASK_EMBEDDINGS_DEVICE")
fi
if [[ -n "${USCODE_MODAL_CODEX_VECTOR_INDEX_PATH:-}" ]]; then
  EXTRA_CODEX_ARGS+=(--codex-vector-index-path "$USCODE_MODAL_CODEX_VECTOR_INDEX_PATH")
fi
PARALLEL_SCOPES="${USCODE_MODAL_CODEX_PARALLEL_SCOPES:-compiler_parser,ir_decompiler,frame_logic}"
if [[ -n "$PARALLEL_SCOPES" ]]; then
  EXTRA_CODEX_ARGS+=(--codex-parallel-scopes "$PARALLEL_SCOPES")
fi

mkdir -p "$ROOT/workspace/test-logs"
{
  printf '%s starting %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RUN_ID"
  cd "$ROOT" || exit 2
  python3 -m ipfs_datasets_py.optimizers.logic_theorem_optimizer.uscode_modal_daemon_runner \
    --loop-role paired \
    --run-id "$RUN_ID" \
    --duration-seconds "${USCODE_MODAL_DURATION_SECONDS:-1800}" \
    --train-count "${USCODE_MODAL_TRAIN_COUNT:-4}" \
    --validation-count "${USCODE_MODAL_VALIDATION_COUNT:-4}" \
    --max-inner-iterations "${USCODE_MODAL_MAX_INNER_ITERATIONS:-2}" \
    --max-items "${USCODE_MODAL_MAX_ITEMS:-1}" \
    --learning-rate "${USCODE_MODAL_LEARNING_RATE:-0.35}" \
    --autoencoder-device "${USCODE_MODAL_AUTOENCODER_DEVICE:-auto}" \
    --poll-seconds "${USCODE_MODAL_POLL_SECONDS:-5}" \
    --test-every-cycles "${USCODE_MODAL_TEST_EVERY_CYCLES:-12}" \
    --codex-exec-mode "${USCODE_MODAL_CODEX_EXEC_MODE:-codex_cli}" \
    --codex-command "${CODEX_BIN:-codex}" \
    --codex-model "${USCODE_MODAL_CODEX_MODEL:-gpt-5.3-codex}" \
    --codex-apply-mode "${USCODE_MODAL_CODEX_APPLY_MODE:-apply_to_main}" \
    --codex-commit-mode "${USCODE_MODAL_CODEX_COMMIT_MODE:-commit_applied}" \
    --codex-sandbox "${USCODE_MODAL_CODEX_SANDBOX:-danger-full-access}" \
    --codex-timeout-seconds "${USCODE_MODAL_CODEX_TIMEOUT_SECONDS:-900}" \
    --paired-launch-delay-seconds "${USCODE_MODAL_PAIRED_LAUNCH_DELAY_SECONDS:-10}" \
    --paired-poll-seconds "${USCODE_MODAL_PAIRED_POLL_SECONDS:-5}" \
    --paired-grace-seconds "${USCODE_MODAL_PAIRED_GRACE_SECONDS:-1200}" \
    "${EXTRA_CODEX_ARGS[@]}"
  rc=$?
  printf '%s finished %s rc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RUN_ID" "$rc"
  exit "$rc"
} >>"$LOG" 2>&1
