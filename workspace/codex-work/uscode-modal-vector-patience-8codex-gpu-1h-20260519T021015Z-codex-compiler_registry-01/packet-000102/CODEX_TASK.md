# packet-000102

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000102/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000102/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000102-20260519_031330

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e33f32b7dbb12e8f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e33f32b7dbb12e8f` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-62ae8a4efff7f361", "predicted_family": "temporal", "priority": 0.955521777922, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic", "target_probability": 0.044478222078}`
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-a0d46f8461636298", "predicted_family": "frame", "priority": 0.952677707098, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic", "target_probability": 0.047322292902}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-a6a45b6964189d34", "predicted_family": "frame", "priority": 0.990510177762, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic", "target_probability": 0.009489822238}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
