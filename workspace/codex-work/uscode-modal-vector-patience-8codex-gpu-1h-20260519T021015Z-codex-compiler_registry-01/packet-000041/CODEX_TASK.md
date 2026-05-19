# packet-000041

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000041/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000041/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000041-20260519_023328

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-47fd00a80cc95aca` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-47fd00a80cc95aca` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.834526153635, "hint_id": "modal-synthesis-231de4ad12f2d6b4", "predicted_family": "conditional_normative", "priority": 0.995339626982, "sample_id": "us-code-16-2103c-66cca91ddd17282c", "target_family": "deontic", "target_probability": 0.004660373018}`
  evidence: `{"family_margin": -0.841584905841, "hint_id": "modal-synthesis-499814512dc6d399", "predicted_family": "conditional_normative", "priority": 0.998230670925, "sample_id": "us-code-41-4106-0cf2c8a4a5764e5b", "target_family": "deontic", "target_probability": 0.001769329075}`
  evidence: `{"family_margin": -0.887458292727, "hint_id": "modal-synthesis-61c8297d105b68f6", "predicted_family": "frame", "priority": 0.989075941968, "sample_id": "us-code-22-6217-3e476128da638bc0", "target_family": "deontic", "target_probability": 0.010924058032}`
- `program-14c955f21dbdef29` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-47fd00a80cc95aca` score `0.976741`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.849721269232, "hint_id": "modal-synthesis-1aa8351e67d672ff", "predicted_family": "conditional_normative", "priority": 0.955478262275, "sample_id": "us-code-42-292x.-f529a098a580370a", "target_family": "temporal", "target_probability": 0.044521737725}`
  evidence: `{"family_margin": -0.082578227591, "hint_id": "modal-synthesis-35620311c31c4ee5", "predicted_family": "frame", "priority": 0.76396698953, "sample_id": "us-code-29-1191c-628b30719a2b4b4e", "target_family": "deontic", "target_probability": 0.23603301047}`
- `program-0d2b4f6aac526054` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-47fd00a80cc95aca` score `0.96269`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-551240fcff75a2e0", "predicted_family": "frame", "priority": 0.710631513026, "sample_id": "us-code-36-154108-10b5a65ddc888004", "target_family": "deontic", "target_probability": 0.289368486974}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-6843de679b0332f8", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-25-746-88b773e186c78138", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.044951128918, "hint_id": "modal-synthesis-73a4c6b0a3c0d0ba", "predicted_family": "deontic", "priority": 0.521318110165, "sample_id": "us-code-20-2569-bdccc2d39a45b47e", "target_family": "deontic", "target_probability": 0.478681889835}`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-af20dfe3adb60419", "predicted_family": "frame", "priority": 0.951939490933, "sample_id": "us-code-30-208-2-aa31c042c6e309e5", "target_family": "temporal", "target_probability": 0.048060509067}`
- `program-126a60861c0d27b2` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-47fd00a80cc95aca` score `0.952813`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-35a480a07ce7f233", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-7-1763-b4f29272663c1fdc", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-8ac3db52dddac29e", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-12-1020d-f5596289cb58637a", "target_family": "frame", "target_probability": 0.470915888067}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
