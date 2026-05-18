# packet-000077

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000077/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000077/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000077-20260518_192054

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-1e25cb7a9e68ae56` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1e25cb7a9e68ae56` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1c426d7a29641fc9", "predicted_family": "temporal", "priority": 0.500067677137, "sample_id": "us-code-48-1422b.-1024d577005506f9", "target_family": "deontic", "target_probability": 0.499932322863}`
  evidence: `{"family_margin": -0.730997206769, "hint_id": "modal-synthesis-94656daa1a588eb7", "predicted_family": "temporal", "priority": 0.999966811271, "sample_id": "us-code-12-59-693f71484c6a9a7a", "target_family": "conditional_normative", "target_probability": 3.3188729e-05}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-d3c203521f582ef4", "predicted_family": "deontic", "priority": 0.5924131531, "sample_id": "us-code-46-30525.-99a6422ab828fa0c", "target_family": "conditional_normative", "target_probability": 0.4075868469}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
