# packet-000208

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000208/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000208/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000208-20260519_130322

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-54d89d130ca990dd` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54d89d130ca990dd` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.829552719341, "hint_id": "modal-synthesis-04a4e4c2401877c5", "predicted_family": "conditional_normative", "priority": 0.979552719341, "sample_id": "us-code-26-3503-c8327a9a01871766", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.998666367346, "hint_id": "modal-synthesis-f56d1ef422763208", "predicted_family": "frame", "priority": 1.148666367346, "sample_id": "us-code-16-2603-bcfd65caaa9561e6", "target_family": "temporal"}`
- `program-6f49f7ff8c3eb0fa` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54d89d130ca990dd` score `0.994745`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ea9d9b7f24815995", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-42-10200.-91ec933481f4ed65", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999705086765, "hint_id": "modal-synthesis-f3132f27be2da555", "predicted_family": "frame", "priority": 1.149705086765, "sample_id": "us-code-42-414.-2a783382bd72bea8", "target_family": "conditional_normative"}`
- `program-ca4b740ef94554ec` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54d89d130ca990dd` score `0.973247`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.236958646552, "hint_id": "modal-synthesis-6711940bef81a99d", "predicted_family": "frame", "priority": 0.386958646552, "sample_id": "us-code-10-8896-be9d438fb8cac68a", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-8c6f2fecbd2bc2a9", "predicted_family": "frame", "priority": 0.982441698483, "sample_id": "us-code-40-5103-46b4843dca9dca6b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.640998164291, "hint_id": "modal-synthesis-b326ec86bc5aa5c1", "predicted_family": "temporal", "priority": 0.790998164291, "sample_id": "us-code-42-3505c.-45b35f1c498964b6", "target_family": "deontic"}`
- `program-63fda1224492c35c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54d89d130ca990dd` score `0.958246`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.99872993958, "hint_id": "modal-synthesis-268c3c2a84d4a7dd", "predicted_family": "alethic", "priority": 1.14872993958, "sample_id": "us-code-16-971d-8be9f90451757eeb", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.391262453299, "hint_id": "modal-synthesis-532e2bb56d587c8c", "predicted_family": "deontic", "priority": 0.541262453299, "sample_id": "us-code-25-1522-a7af7b78aeccf308", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.819471463415, "hint_id": "modal-synthesis-a2449d66af8cd7e1", "predicted_family": "frame", "priority": 0.969471463415, "sample_id": "us-code-42-7546.-f2898bded36e826a", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
