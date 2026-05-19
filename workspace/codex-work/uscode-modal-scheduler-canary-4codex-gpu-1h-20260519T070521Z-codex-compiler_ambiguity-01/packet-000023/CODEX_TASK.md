# packet-000023

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_ambiguity-01/packet-000023/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_ambiguity-01/packet-000023/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000023-20260519_070727

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-00a8fe83d71344b2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-00a8fe83d71344b2` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.39599023273, "hint_id": "modal-synthesis-0109b184636c8833", "predicted_family": "frame", "priority": 0.54599023273, "sample_id": "us-code-37-1003-27a3ce51f0d5bf8b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.415268435064, "hint_id": "modal-synthesis-67043b2c22c5fbe6", "predicted_family": "temporal", "priority": 0.565268435064, "sample_id": "us-code-10-2709-1aff355b49ebbf04", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.795302542954, "hint_id": "modal-synthesis-95a935bdde1408bf", "predicted_family": "alethic", "priority": 0.945302542954, "sample_id": "us-code-42-6000-dcd75b3ed70b7a18", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.969650667457, "hint_id": "modal-synthesis-c362da2a43471048", "predicted_family": "temporal", "priority": 1.119650667457, "sample_id": "us-code-49-50101.-bf43ad4fa78dfc58", "target_family": "deontic"}`
- `program-3a7293a72b0a6cbd` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-00a8fe83d71344b2` score `0.960255`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.957471214953, "hint_id": "modal-synthesis-2ff2259db4488e1a", "predicted_family": "frame", "priority": 1.107471214953, "sample_id": "us-code-33-2341a-994f6f747bb40821", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.201545898387, "hint_id": "modal-synthesis-b5bbcfb34d6db613", "predicted_family": "frame", "priority": 0.351545898387, "sample_id": "us-code-36-150402-30542ec4e64a3fa9", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.370263121745, "hint_id": "modal-synthesis-e196aa613da1fbd7", "predicted_family": "frame", "priority": 0.520263121745, "sample_id": "us-code-44-2909.-f0577602d56b513a", "target_family": "deontic"}`
- `program-ec9ae5d4052e4ab0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-00a8fe83d71344b2` score `0.927434`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.99421734177, "hint_id": "modal-synthesis-48d3c4514af7158e", "predicted_family": "frame", "priority": 1.14421734177, "sample_id": "us-code-33-2282f-4795ec70b8a5c6da", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.26204093192, "hint_id": "modal-synthesis-fc0e9198bcb617dc", "predicted_family": "frame", "priority": 0.41204093192, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
