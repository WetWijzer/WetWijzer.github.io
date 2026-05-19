# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-26f7276b79d52004`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","epistemic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-26f7276b79d52004` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.804241122689`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-6928.-fc1e9d40184ee8c6, us-code-2-141b-878bad9540f78ffc, us-code-25-4044-053049e05567f13c`
  evidence: `{"family_margin": -0.99580361114, "hint_id": "modal-synthesis-114103df8fddba44", "predicted_family": "epistemic", "priority": 1.14580361114, "sample_id": "us-code-42-6928.-fc1e9d40184ee8c6", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-53fbd8aed26e7cf8", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-25-4044-053049e05567f13c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.966919756926, "hint_id": "modal-synthesis-a6bcec1bd16be5a4", "predicted_family": "frame", "priority": 1.116919756926, "sample_id": "us-code-2-141b-878bad9540f78ffc", "target_family": "temporal"}`
