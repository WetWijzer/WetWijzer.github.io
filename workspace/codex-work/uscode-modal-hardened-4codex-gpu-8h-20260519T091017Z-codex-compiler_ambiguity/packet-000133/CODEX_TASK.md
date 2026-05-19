# packet-000133

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000133/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000133/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000133-20260519_113816

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-64c833bbee5986cc` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal","epistemic->epistemic","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-64c833bbee5986cc` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.810658779605, "hint_id": "modal-synthesis-252d065456d176a5", "predicted_family": "deontic", "priority": 0.960658779605, "sample_id": "us-code-16-580m-b422f95353b28b31", "target_family": "frame"}`
  evidence: `{"family_margin": -0.534026866368, "hint_id": "modal-synthesis-49edd4edf940450d", "predicted_family": "deontic", "priority": 0.684026866368, "sample_id": "us-code-16-51-a3778f7455c8838c", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-511302299519c391", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-38-3601-a493eaa250a21490", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.844944355229, "hint_id": "modal-synthesis-c193b8bcc9e594c9", "predicted_family": "frame", "priority": 0.994944355229, "sample_id": "us-code-25-3205-82844da2fd01f148", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
