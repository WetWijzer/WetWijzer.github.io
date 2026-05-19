# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-55b498195f066563`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->dynamic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-55b498195f066563` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.886323704832`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-31-3512-072f35dad3173e73, us-code-22-286n-402424f4edc189eb, us-code-15-1693e-b7074521c1c5667d`
  evidence: `{"family_margin": -0.220358909223, "hint_id": "modal-synthesis-5820c07fa2f9e345", "predicted_family": "deontic", "priority": 0.370358909223, "sample_id": "us-code-15-1693e-b7074521c1c5667d", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.988612205682, "hint_id": "modal-synthesis-ed98dd750b96c422", "predicted_family": "frame", "priority": 1.138612205682, "sample_id": "us-code-22-286n-402424f4edc189eb", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.99999999959, "hint_id": "modal-synthesis-fcbc60c389cf7051", "predicted_family": "temporal", "priority": 1.14999999959, "sample_id": "us-code-31-3512-072f35dad3173e73", "target_family": "deontic"}`
- `program-49c3266926e8d045`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-55b498195f066563` score `0.973494`
  loss: `autoencoder_residual_cluster` = `0.648850513076`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-2376-dbe68d9eaadbdf8f, us-code-42-19136.-5be4eec675d8c9df`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-3eab01d131e91c3f", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-42-19136.-5be4eec675d8c9df", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997701026152, "hint_id": "modal-synthesis-e10c1ff1d449df9a", "predicted_family": "frame", "priority": 1.147701026152, "sample_id": "us-code-22-2376-dbe68d9eaadbdf8f", "target_family": "epistemic"}`
- `program-62686180870bdaa4`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-55b498195f066563` score `0.972592`
  loss: `autoencoder_residual_cluster` = `0.856483624977`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-3066-23903d581786c56b, us-code-43-856.-bc45718a44cb6ae5`
  evidence: `{"family_margin": -0.982287931766, "hint_id": "modal-synthesis-42ca1995d3b6a83e", "predicted_family": "frame", "priority": 1.132287931766, "sample_id": "us-code-10-3066-23903d581786c56b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-8efe83870f38a183", "predicted_family": "temporal", "priority": 0.580679318188, "sample_id": "us-code-43-856.-bc45718a44cb6ae5", "target_family": "deontic"}`
