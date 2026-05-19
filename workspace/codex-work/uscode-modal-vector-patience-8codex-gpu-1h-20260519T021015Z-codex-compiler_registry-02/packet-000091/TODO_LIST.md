# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-be23481d74e524d6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","conditional_normative->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-be23481d74e524d6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999887100749`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-7b-3-8ae854fe9f3e72d9, us-code-26-894-74fa7b27a39e8036, us-code-16-8463-6556ccc2ee90b2bd`
  evidence: `{"family_margin": -0.999997217738, "hint_id": "modal-synthesis-1ded6352dee7a695", "predicted_family": "conditional_normative", "priority": 0.999999747875, "sample_id": "us-code-7-7b-3-8ae854fe9f3e72d9", "target_family": "deontic", "target_probability": 2.52125e-07}`
  evidence: `{"family_margin": -0.990305853512, "hint_id": "modal-synthesis-21a64810f4cda6e2", "predicted_family": "conditional_normative", "priority": 0.999667677914, "sample_id": "us-code-16-8463-6556ccc2ee90b2bd", "target_family": "temporal", "target_probability": 0.000332322086}`
  evidence: `{"family_margin": -0.996629640808, "hint_id": "modal-synthesis-873d4e9ce89e4548", "predicted_family": "conditional_normative", "priority": 0.999993876458, "sample_id": "us-code-26-894-74fa7b27a39e8036", "target_family": "temporal", "target_probability": 6.123542e-06}`
- `program-580a00fc844b06a3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-be23481d74e524d6` score `0.97896`
  loss: `autoencoder_residual_cluster` = `0.99734026734`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1856e.-b5d3bae319ef5cae, us-code-42-288-8070914136da917f`
  evidence: `{"family_margin": -0.945211372516, "hint_id": "modal-synthesis-b20c103706f3aea4", "predicted_family": "conditional_normative", "priority": 0.996499167617, "sample_id": "us-code-42-288-8070914136da917f", "target_family": "deontic", "target_probability": 0.003500832383}`
  evidence: `{"family_margin": -0.988557778739, "hint_id": "modal-synthesis-c3da42a251f68642", "predicted_family": "frame", "priority": 0.998181367064, "sample_id": "us-code-42-1856e.-b5d3bae319ef5cae", "target_family": "conditional_normative", "target_probability": 0.001818632936}`
- `program-51b9ceda178fd073`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-be23481d74e524d6` score `0.967072`
  loss: `autoencoder_residual_cluster` = `0.898236746535`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-6-621-3530d5bd78adaaad, us-code-12-1735f-19-cf4e11a49208d46c`
  evidence: `{"family_margin": -0.999632873878, "hint_id": "modal-synthesis-98b962ca77f47670", "predicted_family": "temporal", "priority": 0.999833447602, "sample_id": "us-code-6-621-3530d5bd78adaaad", "target_family": "frame", "target_probability": 0.000166552398}`
  evidence: `{"family_margin": -0.542828048963, "hint_id": "modal-synthesis-d1f4bf90c7493f03", "predicted_family": "frame", "priority": 0.796640045467, "sample_id": "us-code-12-1735f-19-cf4e11a49208d46c", "target_family": "conditional_normative", "target_probability": 0.203359954533}`
