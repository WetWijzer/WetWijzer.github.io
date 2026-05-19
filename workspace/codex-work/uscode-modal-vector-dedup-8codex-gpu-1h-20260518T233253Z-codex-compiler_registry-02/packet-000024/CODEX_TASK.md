# packet-000024

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000024/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000024/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-2e29db4d0d826d98` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2e29db4d0d826d98` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.804383280095, "hint_id": "modal-synthesis-05717597d0f51d1e", "predicted_family": "frame", "priority": 0.962053725409, "sample_id": "us-code-20-80e-6f0a800587a2c144", "target_family": "epistemic", "target_probability": 0.037946274591}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-77553c27a761c011", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-20-192-5ed09069c63138ac", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.997295894855, "hint_id": "modal-synthesis-bc8a1b0bc8746d05", "predicted_family": "deontic", "priority": 0.99966533223, "sample_id": "us-code-5-6339-2bc797bee283b898", "target_family": "dynamic", "target_probability": 0.00033466777}`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-ed485c1475a9c3d5", "predicted_family": "frame", "priority": 0.91970811195, "sample_id": "us-code-16-450cc-1-ea8ceb5d23d67cf1", "target_family": "deontic", "target_probability": 0.08029188805}`
- `program-85c40fddfac6bc98` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2e29db4d0d826d98` score `0.966916`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.968177985389, "hint_id": "modal-synthesis-146192c7f5eeb792", "predicted_family": "frame", "priority": 0.999582784843, "sample_id": "us-code-30-22-41b0706c6dfe0563", "target_family": "temporal", "target_probability": 0.000417215157}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-8a7ca58b78c1ef57", "predicted_family": "epistemic", "priority": 0.658902128264, "sample_id": "us-code-2-1612-e16ee1803f4650eb", "target_family": "epistemic", "target_probability": 0.341097871736}`
  evidence: `{"family_margin": -0.845499941677, "hint_id": "modal-synthesis-e031bfb6e7d0b39d", "predicted_family": "frame", "priority": 0.967621045722, "sample_id": "us-code-10-2452-9f8cf05c0b023e33", "target_family": "deontic", "target_probability": 0.032378954278}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
