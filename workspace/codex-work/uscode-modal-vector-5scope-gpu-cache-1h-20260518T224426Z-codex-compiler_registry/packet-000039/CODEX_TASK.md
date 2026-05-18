# packet-000039

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000039/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000039/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000039-20260518_231320

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-44d80e437917805b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-44d80e437917805b` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999999694098, "hint_id": "modal-synthesis-70dca751b6f9a9e7", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-26-4943-da67256c0ed21118", "target_family": "temporal", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.999999958321, "hint_id": "modal-synthesis-8157879d8189ff8b", "predicted_family": "conditional_normative", "priority": 1.0, "sample_id": "us-code-21-812-2eb1864ec2e64b00", "target_family": "frame", "target_probability": 0.0}`
- `program-539df53e023e49e0` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-44d80e437917805b` score `0.992492`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-9edbb953cf28b9bf", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-25-677x-a4b45221cb9ce4af", "target_family": "conditional_normative", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.442067654021, "hint_id": "modal-synthesis-d216f86900033152", "predicted_family": "frame", "priority": 0.779425632039, "sample_id": "us-code-33-496-00362c8ed02df86c", "target_family": "deontic", "target_probability": 0.220574367961}`
- `program-045297614e60fbfd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-44d80e437917805b` score `0.992392`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.880748106853, "hint_id": "modal-synthesis-456e80df236e2422", "predicted_family": "conditional_normative", "priority": 0.999992695174, "sample_id": "us-code-10-8089-28cfa15b72bab654", "target_family": "frame", "target_probability": 7.304826e-06}`
  evidence: `{"family_margin": -0.999875778583, "hint_id": "modal-synthesis-faf4eb18c5faf395", "predicted_family": "deontic", "priority": 0.999999587126, "sample_id": "us-code-39-3641-75a3f1a463d54a12", "target_family": "frame", "target_probability": 4.12874e-07}`
- `program-3fdc6fc63df6f59b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-44d80e437917805b` score `0.99025`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.337803377474, "hint_id": "modal-synthesis-9c466e97da7b6f43", "predicted_family": "deontic", "priority": 0.803406302808, "sample_id": "us-code-26-2207A-7ad298682b335ae1", "target_family": "conditional_normative", "target_probability": 0.196593697192}`
  evidence: `{"family_margin": -0.999999163045, "hint_id": "modal-synthesis-dcd0351a4b01c7bf", "predicted_family": "deontic", "priority": 0.999999997939, "sample_id": "us-code-47-219.-09b0a2804ba5c011", "target_family": "temporal", "target_probability": 2.061e-09}`
- `program-3e47abbbbc93b919` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-44d80e437917805b` score `0.990224`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.993925355751, "hint_id": "modal-synthesis-55e6af28d1698922", "predicted_family": "deontic", "priority": 0.999993893074, "sample_id": "us-code-22-503-cc8b5baed9ddff5e", "target_family": "temporal", "target_probability": 6.106926e-06}`
  evidence: `{"family_margin": -0.69082040919, "hint_id": "modal-synthesis-6e1670a96bedc9cc", "predicted_family": "deontic", "priority": 0.845590404021, "sample_id": "us-code-15-78aa-01088ad520ec2450", "target_family": "frame", "target_probability": 0.154409595979}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
