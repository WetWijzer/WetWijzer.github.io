# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-a08a3003a64043be`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a08a3003a64043be` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.748025563397`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-7351d-4e93e049fc664c18, us-code-42-14101.-a5beabd50f2754c9, us-code-33-1107-bb564d15a0040608`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-1ae071a51d65e34f", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-42-14101.-a5beabd50f2754c9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.981612997966, "hint_id": "modal-synthesis-2c7c58cad1f97a64", "predicted_family": "frame", "priority": 1.131612997966, "sample_id": "us-code-20-7351d-4e93e049fc664c18", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.224993730737, "hint_id": "modal-synthesis-69750f8543d17641", "predicted_family": "frame", "priority": 0.374993730737, "sample_id": "us-code-33-1107-bb564d15a0040608", "target_family": "deontic"}`
