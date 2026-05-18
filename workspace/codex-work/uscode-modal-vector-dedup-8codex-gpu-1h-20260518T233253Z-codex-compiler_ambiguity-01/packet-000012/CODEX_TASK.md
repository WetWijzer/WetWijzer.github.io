# packet-000012

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000012/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000012/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000012-20260518_233406

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-481729935f73954b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-481729935f73954b` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-207eecb2dff41a7d", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-22-127-239ab62aacc72ba4", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.182896227451, "hint_id": "modal-synthesis-aed597e6d328fcc6", "predicted_family": "frame", "priority": 0.332896227451, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
