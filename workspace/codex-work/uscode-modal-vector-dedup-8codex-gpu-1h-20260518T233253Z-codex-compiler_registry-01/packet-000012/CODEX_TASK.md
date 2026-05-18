# packet-000012

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000012/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000012/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000012-20260518_233406

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-9725683f62b1cfab` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9725683f62b1cfab` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.182896227451, "hint_id": "modal-synthesis-a175fb8e874e6b50", "predicted_family": "frame", "priority": 0.718066547666, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d", "target_family": "deontic", "target_probability": 0.281933452334}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-eb7b1a9b69b398fd", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-12-639-a6faf86b06383bb9", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-ee015ca86c492a99", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-22-127-239ab62aacc72ba4", "target_family": "temporal", "target_probability": 0.008091643722}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
