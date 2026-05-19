# packet-000058

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000058/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000058/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000058-20260519_023234

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-114e1fc32cce625c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-114e1fc32cce625c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.841584905841, "hint_id": "modal-synthesis-678caad3a584ab9d", "predicted_family": "conditional_normative", "priority": 0.991584905841, "sample_id": "us-code-41-4106-0cf2c8a4a5764e5b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.887458292727, "hint_id": "modal-synthesis-7ff8d1a9e18edc66", "predicted_family": "frame", "priority": 1.037458292727, "sample_id": "us-code-22-6217-3e476128da638bc0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.834526153635, "hint_id": "modal-synthesis-d73804ed22f08516", "predicted_family": "conditional_normative", "priority": 0.984526153635, "sample_id": "us-code-16-2103c-66cca91ddd17282c", "target_family": "deontic"}`
- `program-1176f13055fdedf2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-114e1fc32cce625c` score `0.978609`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.849721269232, "hint_id": "modal-synthesis-2abd074a0cb99a7e", "predicted_family": "conditional_normative", "priority": 0.999721269232, "sample_id": "us-code-42-292x.-f529a098a580370a", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.082578227591, "hint_id": "modal-synthesis-54fcf3abf80783e3", "predicted_family": "frame", "priority": 0.232578227591, "sample_id": "us-code-29-1191c-628b30719a2b4b4e", "target_family": "deontic"}`
- `program-fb583ed2fc9f1277` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-114e1fc32cce625c` score `0.955082`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.521443876084, "hint_id": "modal-synthesis-2435c30f3bf58c91", "predicted_family": "alethic", "priority": 0.671443876084, "sample_id": "us-code-31-1531-68d5886a05c9885e", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-bc73b488939a36e9", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-20-2701-dd44f5dab9f1f127", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
