# packet-000019

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000019/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000019/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000019-20260518_233441

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-748277528fe79902` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-748277528fe79902` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.997538709134, "hint_id": "modal-synthesis-785f19662bc2ac33", "predicted_family": "deontic", "priority": 0.998770604452, "sample_id": "us-code-10-1030-6ebd847628f9a7da", "target_family": "frame", "target_probability": 0.001229395548}`
  evidence: `{"family_margin": -0.999999999835, "hint_id": "modal-synthesis-7a5f641fb1bda708", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-15-657d-be08838ed78ea48c", "target_family": "temporal", "target_probability": 5e-12}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
