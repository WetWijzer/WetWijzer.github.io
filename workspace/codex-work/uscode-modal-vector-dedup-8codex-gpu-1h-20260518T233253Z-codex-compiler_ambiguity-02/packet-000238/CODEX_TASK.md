# packet-000238

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000238/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000238/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000238-20260519_002939

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a08a3003a64043be` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a08a3003a64043be` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-1ae071a51d65e34f", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-42-14101.-a5beabd50f2754c9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.981612997966, "hint_id": "modal-synthesis-2c7c58cad1f97a64", "predicted_family": "frame", "priority": 1.131612997966, "sample_id": "us-code-20-7351d-4e93e049fc664c18", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.224993730737, "hint_id": "modal-synthesis-69750f8543d17641", "predicted_family": "frame", "priority": 0.374993730737, "sample_id": "us-code-33-1107-bb564d15a0040608", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
