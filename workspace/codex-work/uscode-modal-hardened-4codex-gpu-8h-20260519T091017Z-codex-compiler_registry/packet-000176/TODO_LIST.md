# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-0b14b47a5f3a2e42`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0b14b47a5f3a2e42` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.780099702777`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-2405-c618ad908c655a89, us-code-38-3221-d0911ad7952419ce, us-code-16-410ss-1-196de05d18239619`
  evidence: `{"family_margin": -0.219959544438, "hint_id": "modal-synthesis-74a9d275f846f788", "predicted_family": "frame", "priority": 0.655439004335, "sample_id": "us-code-16-410ss-1-196de05d18239619", "target_family": "deontic", "target_probability": 0.344560995665}`
  evidence: `{"family_margin": -0.795861109774, "hint_id": "modal-synthesis-8001a2c8e519b9cd", "predicted_family": "deontic", "priority": 0.962401153588, "sample_id": "us-code-12-2405-c618ad908c655a89", "target_family": "dynamic", "target_probability": 0.037598846412}`
  evidence: `{"family_margin": -0.085397246028, "hint_id": "modal-synthesis-a86a664246ec0785", "predicted_family": "deontic", "priority": 0.722458950409, "sample_id": "us-code-38-3221-d0911ad7952419ce", "target_family": "temporal", "target_probability": 0.277541049591}`
