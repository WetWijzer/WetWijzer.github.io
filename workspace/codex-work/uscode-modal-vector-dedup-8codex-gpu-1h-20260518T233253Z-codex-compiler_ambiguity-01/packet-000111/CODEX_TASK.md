# packet-000111

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000111/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000111/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000111-20260519_003314

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-61d5b8c68680128d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-61d5b8c68680128d` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.57053542844, "hint_id": "modal-synthesis-3cdb14c6df69ceab", "predicted_family": "frame", "priority": 0.72053542844, "sample_id": "us-code-10-1502-bc96eb40bcb85230", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.353962738201, "hint_id": "modal-synthesis-3e3ae492f9bc841e", "predicted_family": "conditional_normative", "priority": 0.503962738201, "sample_id": "us-code-42-614.-55a5addd3de258c0", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-8dc0d69ed316f01d", "predicted_family": "frame", "priority": 0.359117456717, "sample_id": "us-code-8-1440a-f91958d13012a26a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-ad2e09536458d964", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-8-239-b3ac1f025fea6153", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
