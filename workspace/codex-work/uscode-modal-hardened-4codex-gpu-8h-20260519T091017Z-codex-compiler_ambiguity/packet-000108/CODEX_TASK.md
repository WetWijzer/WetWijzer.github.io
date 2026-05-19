# packet-000108

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000108/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000108/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000108-20260519_111337

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-686e83a07f71f9b7` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-686e83a07f71f9b7` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.955419320628, "hint_id": "modal-synthesis-504c188faf472026", "predicted_family": "alethic", "priority": 1.105419320628, "sample_id": "us-code-15-2625-828287ed4e5bfa4c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.833750467481, "hint_id": "modal-synthesis-a124116375f16f4d", "predicted_family": "deontic", "priority": 0.983750467481, "sample_id": "us-code-42-1962c-a74c16e37e82d6a3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.945786865874, "hint_id": "modal-synthesis-b0166aedcdab44cf", "predicted_family": "frame", "priority": 1.095786865874, "sample_id": "us-code-29-718-b58562ccab445aec", "target_family": "conditional_normative"}`
- `program-b646f04aa15b7910` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-686e83a07f71f9b7` score `0.97344`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.453607166209, "hint_id": "modal-synthesis-ca46fd3c2cce150f", "predicted_family": "frame", "priority": 0.603607166209, "sample_id": "us-code-15-4601-6e7f8f28b8562add", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.180973014, "hint_id": "modal-synthesis-fa883b5d7e707f69", "predicted_family": "conditional_normative", "priority": 0.330973014, "sample_id": "us-code-42-300gg-5bf9852741930d4a", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
