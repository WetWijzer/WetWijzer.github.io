# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-b9c605e649bbb05b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b9c605e649bbb05b` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.823652026402`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-12604.-1d234db6b2b96dae, us-code-16-5201-032991f8a1d37d4e, us-code-5-2904-6a34aeff644bc118, us-code-20-6432-cef881b033466057`
  evidence: `{"family_margin": -0.135415317285, "hint_id": "modal-synthesis-08ccd55d69028a7d", "predicted_family": "frame", "priority": 0.713309519334, "sample_id": "us-code-5-2904-6a34aeff644bc118", "target_family": "deontic", "target_probability": 0.286690480666}`
  evidence: `{"family_margin": 0.139325101176, "hint_id": "modal-synthesis-4838adc4574081c2", "predicted_family": "temporal", "priority": 0.616855971767, "sample_id": "us-code-20-6432-cef881b033466057", "target_family": "temporal", "target_probability": 0.383144028233}`
  evidence: `{"family_margin": -0.983862874993, "hint_id": "modal-synthesis-a9041d55768671cf", "predicted_family": "frame", "priority": 0.996388837802, "sample_id": "us-code-42-12604.-1d234db6b2b96dae", "target_family": "deontic", "target_probability": 0.003611162198}`
  evidence: `{"family_margin": -0.271151104314, "hint_id": "modal-synthesis-c82a825140c015b1", "predicted_family": "deontic", "priority": 0.968053776703, "sample_id": "us-code-16-5201-032991f8a1d37d4e", "target_family": "frame", "target_probability": 0.031946223297}`
- `program-aa904cf61aac79ad`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->alethic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b9c605e649bbb05b` score `0.96244`
  loss: `autoencoder_residual_cluster` = `0.771608166147`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-1715r-858d530b59362134, us-code-41-8506-7ecc8f89ca8b7ea9, us-code-29-1871-44485ec98810815a`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-228a1403129b0f3c", "predicted_family": "frame", "priority": 0.710631513026, "sample_id": "us-code-41-8506-7ecc8f89ca8b7ea9", "target_family": "alethic", "target_probability": 0.289368486974}`
  evidence: `{"family_margin": -0.997162187617, "hint_id": "modal-synthesis-2a45a918a7d72ddd", "predicted_family": "frame", "priority": 0.998858414442, "sample_id": "us-code-12-1715r-858d530b59362134", "target_family": "conditional_normative", "target_probability": 0.001141585558}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-5aeeab2aa5d2d35a", "predicted_family": "temporal", "priority": 0.605334570972, "sample_id": "us-code-29-1871-44485ec98810815a", "target_family": "deontic", "target_probability": 0.394665429028}`
