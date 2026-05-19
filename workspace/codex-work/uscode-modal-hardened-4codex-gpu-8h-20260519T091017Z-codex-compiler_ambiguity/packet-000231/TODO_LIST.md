# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-6ab3c30bd34972f6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6ab3c30bd34972f6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.962175939021`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-4301-f41e0787fba53b0a, us-code-42-7511b.-1d3299a1a442c3ed, us-code-42-1772.-026fbcdf892256fb`
  evidence: `{"family_margin": -0.889025829822, "hint_id": "modal-synthesis-15f36f0f258c8a9f", "predicted_family": "epistemic", "priority": 1.039025829822, "sample_id": "us-code-42-7511b.-1d3299a1a442c3ed", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.54822096945, "hint_id": "modal-synthesis-1bd75e66f97a30f7", "predicted_family": "frame", "priority": 0.69822096945, "sample_id": "us-code-42-1772.-026fbcdf892256fb", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999281017791, "hint_id": "modal-synthesis-fcbc8b0869f1e127", "predicted_family": "frame", "priority": 1.149281017791, "sample_id": "us-code-38-4301-f41e0787fba53b0a", "target_family": "temporal"}`
