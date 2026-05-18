# packet-000375

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000375/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000375/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000375-20260518_200847

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-d54a92a96009beaf` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d54a92a96009beaf` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-003d5945a2786d35", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999999646, "hint_id": "modal-synthesis-5541a584b90f7d70", "predicted_family": "temporal", "priority": 1.149999999646, "sample_id": "us-code-16-2622-7b3b0068d25f5128", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
