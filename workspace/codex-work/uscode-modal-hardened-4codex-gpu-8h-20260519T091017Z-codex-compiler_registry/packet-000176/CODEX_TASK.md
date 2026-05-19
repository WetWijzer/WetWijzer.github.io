# packet-000176

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000176/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000176/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-0b14b47a5f3a2e42` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0b14b47a5f3a2e42` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.219959544438, "hint_id": "modal-synthesis-74a9d275f846f788", "predicted_family": "frame", "priority": 0.655439004335, "sample_id": "us-code-16-410ss-1-196de05d18239619", "target_family": "deontic", "target_probability": 0.344560995665}`
  evidence: `{"family_margin": -0.795861109774, "hint_id": "modal-synthesis-8001a2c8e519b9cd", "predicted_family": "deontic", "priority": 0.962401153588, "sample_id": "us-code-12-2405-c618ad908c655a89", "target_family": "dynamic", "target_probability": 0.037598846412}`
  evidence: `{"family_margin": -0.085397246028, "hint_id": "modal-synthesis-a86a664246ec0785", "predicted_family": "deontic", "priority": 0.722458950409, "sample_id": "us-code-38-3221-d0911ad7952419ce", "target_family": "temporal", "target_probability": 0.277541049591}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
