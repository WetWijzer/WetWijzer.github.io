# packet-000111

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000111/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000111/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260518_193637

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-cf8b7ab670ac7a3c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["temporal->conditional_normative","temporal->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-cf8b7ab670ac7a3c` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999999999976, "hint_id": "modal-synthesis-219dd78588234f67", "predicted_family": "temporal", "priority": 0.999999999995, "sample_id": "us-code-31-5312-039372e5e9300b7d", "target_family": "conditional_normative", "target_probability": 5e-12}`
  evidence: `{"family_margin": -0.737725781832, "hint_id": "modal-synthesis-dfc7b4dbba5a2824", "predicted_family": "temporal", "priority": 0.884532899632, "sample_id": "us-code-43-270-9753303f57791aad", "target_family": "conditional_normative", "target_probability": 0.115467100368}`
  evidence: `{"family_margin": -0.999999999986, "hint_id": "modal-synthesis-f55db941552930d4", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "target_family": "epistemic", "target_probability": 0.0}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
