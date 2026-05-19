# packet-000020

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000020/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000020/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000020-20260518_234014

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-fa00c5c790c2003b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa00c5c790c2003b` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.40110022983, "hint_id": "modal-synthesis-a16e720df4d29b58", "predicted_family": "frame", "priority": 0.55110022983, "sample_id": "us-code-10-909-22586a547806bf91", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-a742066ca4bea1b1", "predicted_family": "frame", "priority": 0.19007547842, "sample_id": "us-code-42-300a-e57ccd658257dc26", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.817522388616, "hint_id": "modal-synthesis-db2abfe7e914fdc0", "predicted_family": "frame", "priority": 0.967522388616, "sample_id": "us-code-13-3-554d264efed79ab1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.876709281778, "hint_id": "modal-synthesis-f93a029e326b1ecb", "predicted_family": "deontic", "priority": 1.026709281778, "sample_id": "us-code-22-290n-3-2b067e975d5b088d", "target_family": "temporal"}`
- `program-470c75c37e0c2892` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa00c5c790c2003b` score `0.957249`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.031508900693, "hint_id": "modal-synthesis-9c7513ddbbdea9a3", "predicted_family": "frame", "priority": 0.181508900693, "sample_id": "us-code-16-10-1e096a226413d70c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.493804106414, "hint_id": "modal-synthesis-a2ef1009c479135f", "predicted_family": "deontic", "priority": 0.643804106414, "sample_id": "us-code-25-5614-36b3f84152c54706", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a6ef60b71c5630e7", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-18-225-94b2deec9f016491", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
