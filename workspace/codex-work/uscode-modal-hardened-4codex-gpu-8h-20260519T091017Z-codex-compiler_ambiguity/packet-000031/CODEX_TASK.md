# packet-000031

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000031/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000031/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-54cd2c2e405b10be` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","deontic->frame","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54cd2c2e405b10be` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2403288f11cc5b39", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-6-677g-31d2665e1caccc9c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.856149561517, "hint_id": "modal-synthesis-5e83d1c78190b68e", "predicted_family": "deontic", "priority": 1.006149561517, "sample_id": "us-code-26-651-ec1f77fec5fb0a62", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.572604759408, "hint_id": "modal-synthesis-a7141e5daa46d622", "predicted_family": "conditional_normative", "priority": 0.722604759408, "sample_id": "us-code-16-410aaa-50-d93ecd7b2c265bca", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.443094037392, "hint_id": "modal-synthesis-fd444a6f940ffb32", "predicted_family": "deontic", "priority": 0.593094037392, "sample_id": "us-code-42-8834.-21377f76b0372f94", "target_family": "frame"}`
- `program-9859927cac8fe290` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54cd2c2e405b10be` score `0.91926`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": 0.043571664466, "hint_id": "modal-synthesis-77caba25503a5594", "predicted_family": "deontic", "priority": 0.106428335534, "sample_id": "us-code-42-290dd.-2810fb987912153f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b0c9e44ad236cd79", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-20-5701-168cf2ab50ae0346", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
