# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-7302b7d5822b16c0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7302b7d5822b16c0` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.022969449976`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-4145-29f1b6e849d52610, us-code-12-5370-7a08b2959e7f0721, us-code-10-1207-3747e5081e568c1e`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-298c6ebb4fb7b30c", "predicted_family": "frame", "priority": 0.93969827777, "sample_id": "us-code-10-1207-3747e5081e568c1e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.989479571796, "hint_id": "modal-synthesis-4b4035174ecf0498", "predicted_family": "conditional_normative", "priority": 1.139479571796, "sample_id": "us-code-12-4145-29f1b6e849d52610", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.839730500363, "hint_id": "modal-synthesis-fc47177039b2c47f", "predicted_family": "deontic", "priority": 0.989730500363, "sample_id": "us-code-12-5370-7a08b2959e7f0721", "target_family": "frame"}`
- `program-4afb8d332a1053f9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7302b7d5822b16c0` score `0.983912`
  loss: `autoencoder_residual_cluster` = `0.970356379202`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1104.-e394bd5517bbd020, us-code-38-3678-3d85bc7a52705388, us-code-43-373d.-735b38078b23dd60`
  evidence: `{"family_margin": -0.993227253513, "hint_id": "modal-synthesis-4ff962f5ac69da3c", "predicted_family": "conditional_normative", "priority": 1.143227253513, "sample_id": "us-code-42-1104.-e394bd5517bbd020", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.980421678302, "hint_id": "modal-synthesis-c1d92da5ce668def", "predicted_family": "frame", "priority": 1.130421678302, "sample_id": "us-code-38-3678-3d85bc7a52705388", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.487420205792, "hint_id": "modal-synthesis-c892197724848db5", "predicted_family": "frame", "priority": 0.637420205792, "sample_id": "us-code-43-373d.-735b38078b23dd60", "target_family": "temporal"}`
- `program-d3200538e7021e43`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7302b7d5822b16c0` score `0.969748`
  loss: `autoencoder_residual_cluster` = `0.802193857688`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1490h.-f8a747e85ba922c7, us-code-49-60143.-bbe39953f892dc35`
  evidence: `{"family_margin": -0.357890198984, "hint_id": "modal-synthesis-4453c2a38880f716", "predicted_family": "deontic", "priority": 0.507890198984, "sample_id": "us-code-49-60143.-bbe39953f892dc35", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.946497516393, "hint_id": "modal-synthesis-a90c3a790030233e", "predicted_family": "conditional_normative", "priority": 1.096497516393, "sample_id": "us-code-42-1490h.-f8a747e85ba922c7", "target_family": "temporal"}`
