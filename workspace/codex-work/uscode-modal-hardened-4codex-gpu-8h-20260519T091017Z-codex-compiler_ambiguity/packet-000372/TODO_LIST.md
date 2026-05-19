# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-f6c8228ddadc1de8`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f6c8228ddadc1de8` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.904070316392`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-46-3303.-262060b4e52c28d7, us-code-43-883.-4cf3c55207a7042d, us-code-2-2182-5a4da71f9b7ed715, us-code-50-3533.-fbe9761d5d5aa91b`
  evidence: `{"family_margin": -0.914900774437, "hint_id": "modal-synthesis-01fa4343debf31d6", "predicted_family": "deontic", "priority": 1.064900774437, "sample_id": "us-code-43-883.-4cf3c55207a7042d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.988780738882, "hint_id": "modal-synthesis-7d44737360a31641", "predicted_family": "frame", "priority": 1.138780738882, "sample_id": "us-code-46-3303.-262060b4e52c28d7", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.75246836579, "hint_id": "modal-synthesis-8973b7e60133c099", "predicted_family": "deontic", "priority": 0.90246836579, "sample_id": "us-code-2-2182-5a4da71f9b7ed715", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.360131386457, "hint_id": "modal-synthesis-93d5d678bc638306", "predicted_family": "alethic", "priority": 0.510131386457, "sample_id": "us-code-50-3533.-fbe9761d5d5aa91b", "target_family": "deontic"}`
