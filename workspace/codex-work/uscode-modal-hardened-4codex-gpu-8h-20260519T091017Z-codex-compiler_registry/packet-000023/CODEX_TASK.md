# packet-000023

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000023/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000023/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000023-20260519_112954

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-6adb2f0085805d94` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.98293533675, "hint_id": "modal-synthesis-50cc0076dfa2fb69", "predicted_family": "frame", "priority": 0.999335540198, "sample_id": "us-code-29-1851-f2b8bca48c79ea5b", "target_family": "epistemic", "target_probability": 0.000664459802}`
  evidence: `{"family_margin": -0.788983986003, "hint_id": "modal-synthesis-f0fea968e172dbe9", "predicted_family": "frame", "priority": 0.949104962523, "sample_id": "us-code-20-1087cc-7df79972ab6270a9", "target_family": "deontic", "target_probability": 0.050895037477}`
- `program-459322b0177702ff` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `0.932947`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.376889143959, "hint_id": "modal-synthesis-3a31ed870ee84a20", "predicted_family": "frame", "priority": 0.917791077775, "sample_id": "us-code-22-4071k-55a17ec8c5e3db3e", "target_family": "temporal", "target_probability": 0.082208922225}`
  evidence: `{"family_margin": -0.992896805877, "hint_id": "modal-synthesis-56a34ac03a423e9e", "predicted_family": "frame", "priority": 0.99932880629, "sample_id": "us-code-50-855.-6b18aaa5a6c9cf83", "target_family": "deontic", "target_probability": 0.00067119371}`
  evidence: `{"family_margin": -0.436671018642, "hint_id": "modal-synthesis-6d2b8d4def6ae606", "predicted_family": "temporal", "priority": 0.968306905012, "sample_id": "us-code-43-326.-5500eb218f8a7886", "target_family": "conditional_normative", "target_probability": 0.031693094988}`
  evidence: `{"family_margin": -0.18481454784, "hint_id": "modal-synthesis-c87cbfc171aa17a2", "predicted_family": "frame", "priority": 0.608725418832, "sample_id": "us-code-50-3305.-3e025318340f6f2a", "target_family": "temporal", "target_probability": 0.391274581168}`
- `program-7449908df84e1d1b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `0.917552`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.907679549796, "hint_id": "modal-synthesis-10c41a9ca37bfa75", "predicted_family": "frame", "priority": 0.999665223016, "sample_id": "us-code-42-1396u-57bec3d2de18e889", "target_family": "deontic", "target_probability": 0.000334776984}`
  evidence: `{"family_margin": -0.495628881718, "hint_id": "modal-synthesis-289dd1c70315c638", "predicted_family": "temporal", "priority": 0.990228790792, "sample_id": "us-code-2-5303-d859402e8a787491", "target_family": "deontic", "target_probability": 0.009771209208}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-83c93de522d2bdcf", "predicted_family": "deontic", "priority": 0.682800890818, "sample_id": "us-code-22-9614-25ece758489d6025", "target_family": "deontic", "target_probability": 0.317199109182}`
  evidence: `{"family_margin": -0.480261147937, "hint_id": "modal-synthesis-8443a92785660a75", "predicted_family": "deontic", "priority": 0.898892389908, "sample_id": "us-code-42-11043.-a349cc422cfb814d", "target_family": "temporal", "target_probability": 0.101107610092}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
