# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-4b8ba2f97fd3af83`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4b8ba2f97fd3af83` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.94265551296`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-460nnn-72-a7c1871912514db1, us-code-50-98h-81e88eb05f5b95c6, us-code-12-2279a-3-e50f61df5c1d28a1`
  evidence: `{"family_margin": -0.9045986346, "hint_id": "modal-synthesis-2f302b86ae856ba3", "predicted_family": "frame", "priority": 0.962374393764, "sample_id": "us-code-50-98h-81e88eb05f5b95c6", "target_family": "deontic", "target_probability": 0.037625606236}`
  evidence: `{"family_margin": -0.663964931589, "hint_id": "modal-synthesis-6104c09fec76b40c", "predicted_family": "deontic", "priority": 0.976748854387, "sample_id": "us-code-16-460nnn-72-a7c1871912514db1", "target_family": "epistemic", "target_probability": 0.023251145613}`
  evidence: `{"family_margin": -0.617309325395, "hint_id": "modal-synthesis-f7916b84e3fe9846", "predicted_family": "frame", "priority": 0.88884329073, "sample_id": "us-code-12-2279a-3-e50f61df5c1d28a1", "target_family": "temporal", "target_probability": 0.11115670927}`
- `program-f4675cc81b476265`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4b8ba2f97fd3af83` score `0.960471`
  loss: `autoencoder_residual_cluster` = `0.751951564185`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-1821-af7b05f2f810f8a5, us-code-33-701l-46fcd24a2e0e46c1`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-078cc2a080eee529", "predicted_family": "conditional_normative", "priority": 0.50390312837, "sample_id": "us-code-33-701l-46fcd24a2e0e46c1", "target_family": "conditional_normative", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-6c274f7de03aef0e", "predicted_family": "frame", "priority": 1.0, "sample_id": "us-code-12-1821-af7b05f2f810f8a5", "target_family": "deontic", "target_probability": 0.0}`
