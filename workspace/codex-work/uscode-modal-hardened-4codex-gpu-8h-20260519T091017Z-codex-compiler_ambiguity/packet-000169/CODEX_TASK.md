# packet-000169

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000169/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000169/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000169-20260519_123909

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a8a34ccf7fb6a9f8` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a8a34ccf7fb6a9f8` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.960878504821, "hint_id": "modal-synthesis-0de2caade2d5d32c", "predicted_family": "frame", "priority": 1.110878504821, "sample_id": "us-code-42-248a.-9261c2a788f1cbcf", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1408b661ad18c091", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-16-1311-014f0ec1c47a5cce", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.972358698454, "hint_id": "modal-synthesis-709cd9561bdb31c0", "predicted_family": "frame", "priority": 1.122358698454, "sample_id": "us-code-10-862-40c2d7c8f9a77d41", "target_family": "temporal"}`
- `program-0e5164c7b779355f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a8a34ccf7fb6a9f8` score `0.988814`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.676448880695, "hint_id": "modal-synthesis-2df2b72b28134769", "predicted_family": "deontic", "priority": 0.826448880695, "sample_id": "us-code-15-1847-830b651eb663dca8", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-60b0932527fe5590", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-7-7424-e7673f78fca9418a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.17371933462, "hint_id": "modal-synthesis-fed884f3607428a0", "predicted_family": "frame", "priority": 0.32371933462, "sample_id": "us-code-34-12404-4c3ffacca50adfcf", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
