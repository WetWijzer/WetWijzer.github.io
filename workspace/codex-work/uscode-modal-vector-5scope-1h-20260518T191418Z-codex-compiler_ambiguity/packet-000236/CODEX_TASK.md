# packet-000236

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000236/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000236/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000236-20260518_193831

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-139849e64ce59278` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-139849e64ce59278` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-a05880749cc9422c", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-29-1662-e7516434dca445ba", "target_family": "frame"}`
  evidence: `{"family_margin": -0.99962738107, "hint_id": "modal-synthesis-b6f7b3b94418499b", "predicted_family": "temporal", "priority": 1.14962738107, "sample_id": "us-code-34-11294-0a6981caa505e06b", "target_family": "frame"}`
  evidence: `{"family_margin": -0.458673661066, "hint_id": "modal-synthesis-ef4b906f91f18367", "predicted_family": "temporal", "priority": 0.608673661066, "sample_id": "us-code-16-831r-67ffc5b229e2bd75", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
