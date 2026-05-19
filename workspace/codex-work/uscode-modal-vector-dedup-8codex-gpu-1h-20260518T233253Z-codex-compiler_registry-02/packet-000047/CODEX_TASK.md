# packet-000047

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000047/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000047/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000047-20260519_002603

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a1795f58ad6c8d01` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a1795f58ad6c8d01` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-9e0bc3d7af9addbd", "predicted_family": "frame", "priority": 0.918078633988, "sample_id": "us-code-25-967b-414b28c838c6ad8b", "target_family": "conditional_normative", "target_probability": 0.081921366012}`
  evidence: `{"family_margin": -0.413068740844, "hint_id": "modal-synthesis-e1fa69c7a47a62ea", "predicted_family": "frame", "priority": 0.845251842609, "sample_id": "us-code-43-156.-f144163c12efb2fc", "target_family": "temporal", "target_probability": 0.154748157391}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
