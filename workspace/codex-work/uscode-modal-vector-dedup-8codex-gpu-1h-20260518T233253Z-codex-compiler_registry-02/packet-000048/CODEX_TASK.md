# packet-000048

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000048/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000048/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000048-20260519_003408

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e3b0b7c39dd0f2bb` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e3b0b7c39dd0f2bb` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.353962738201, "hint_id": "modal-synthesis-17e3188a77affe69", "predicted_family": "conditional_normative", "priority": 0.857865866571, "sample_id": "us-code-42-614.-55a5addd3de258c0", "target_family": "temporal", "target_probability": 0.142134133429}`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-a2250076938f973d", "predicted_family": "frame", "priority": 0.677646677915, "sample_id": "us-code-8-1440a-f91958d13012a26a", "target_family": "deontic", "target_probability": 0.322353322085}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-b3c7ec2ab55a87aa", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-8-239-b3ac1f025fea6153", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.57053542844, "hint_id": "modal-synthesis-dec03ff5d700c94e", "predicted_family": "frame", "priority": 0.998950395674, "sample_id": "us-code-10-1502-bc96eb40bcb85230", "target_family": "temporal", "target_probability": 0.001049604326}`
- `program-f980c5932e25d2d4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e3b0b7c39dd0f2bb` score `0.978363`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.19236749042, "hint_id": "modal-synthesis-0a99672ec98c62f3", "predicted_family": "deontic", "priority": 0.511099161425, "sample_id": "us-code-22-290h-1-68644b41d5e5cf83", "target_family": "deontic", "target_probability": 0.488900838575}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-59e4c10f1f3f9221", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-39-3626-c1fe6a2709b0deab", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.999999901971, "hint_id": "modal-synthesis-615074d4453a6b68", "predicted_family": "deontic", "priority": 0.999999958601, "sample_id": "us-code-26-1271-9d2820abfea51ea9", "target_family": "temporal", "target_probability": 4.1399e-08}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
