# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-e87f3a6bcb59a913`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e87f3a6bcb59a913` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.714844187152`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-59ee-1-a6cd77c9bf3393ce, us-code-45-501 to 502.-8e8f2d25c9ff5006, us-code-22-9688-5f6bbc5155d748f5`
  evidence: `{"family_margin": -0.432296025335, "hint_id": "modal-synthesis-9e09c9959586592c", "predicted_family": "frame", "priority": 0.582296025335, "sample_id": "us-code-22-9688-5f6bbc5155d748f5", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.813922215476, "hint_id": "modal-synthesis-e1d73bc04c8ce2ae", "predicted_family": "frame", "priority": 0.963922215476, "sample_id": "us-code-33-59ee-1-a6cd77c9bf3393ce", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.448314320645, "hint_id": "modal-synthesis-fb22508423f9ea3e", "predicted_family": "frame", "priority": 0.598314320645, "sample_id": "us-code-45-501 to 502.-8e8f2d25c9ff5006", "target_family": "temporal"}`
- `program-9bfc1f6749d0cee5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e87f3a6bcb59a913` score `0.965165`
  loss: `autoencoder_residual_cluster` = `0.594603236201`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-298-488dd31bd85d3d5d, us-code-47-334.-69f097820d01d38e, us-code-15-6410-934e3582cffdc47c`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-99401bb9a6c6c796", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-15-6410-934e3582cffdc47c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.993985449933, "hint_id": "modal-synthesis-a8686baaccc866f7", "predicted_family": "frame", "priority": 1.143985449933, "sample_id": "us-code-22-298-488dd31bd85d3d5d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.33982425867, "hint_id": "modal-synthesis-b82f590b14481773", "predicted_family": "temporal", "priority": 0.48982425867, "sample_id": "us-code-47-334.-69f097820d01d38e", "target_family": "conditional_normative"}`
- `program-ec548643b7616c86`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e87f3a6bcb59a913` score `0.936475`
  loss: `autoencoder_residual_cluster` = `0.277803116668`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-41-3901-a0e6f0f39e8159f5, us-code-23-178-7ece24719db412c2, us-code-12-2289-1e358d5edf0d64b7, us-code-49-44806.-394c29631583f2d2`
  evidence: `{"family_margin": -0.274690539061, "hint_id": "modal-synthesis-32b0b952c2560638", "predicted_family": "deontic", "priority": 0.424690539061, "sample_id": "us-code-23-178-7ece24719db412c2", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.279404198743, "hint_id": "modal-synthesis-727774c6358f98e6", "predicted_family": "frame", "priority": 0.429404198743, "sample_id": "us-code-41-3901-a0e6f0f39e8159f5", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.026084716803, "hint_id": "modal-synthesis-952a39d21395efd9", "predicted_family": "alethic", "priority": 0.176084716803, "sample_id": "us-code-12-2289-1e358d5edf0d64b7", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.068966987935, "hint_id": "modal-synthesis-c6eab1b4e0b596b4", "predicted_family": "deontic", "priority": 0.081033012065, "sample_id": "us-code-49-44806.-394c29631583f2d2", "target_family": "deontic"}`
