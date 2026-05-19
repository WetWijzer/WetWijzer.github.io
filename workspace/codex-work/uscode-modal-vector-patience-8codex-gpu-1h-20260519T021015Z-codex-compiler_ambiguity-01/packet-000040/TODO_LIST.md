# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-e70c13db6db4223b`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.105312173367`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-52-10310.-26f34fd94cb731ad, us-code-16-1028-3a1bf3000702288a`
  evidence: `{"family_margin": -0.98344914023, "hint_id": "modal-synthesis-117bf73f21a6f95d", "predicted_family": "frame", "priority": 1.13344914023, "sample_id": "us-code-52-10310.-26f34fd94cb731ad", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-3108d54a22d6a397", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-16-1028-3a1bf3000702288a", "target_family": "temporal"}`
- `program-f1a845d42fcb293f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `0.971663`
  loss: `autoencoder_residual_cluster` = `0.96961678411`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-34-10153-56c96555be0f0204, us-code-48-1668.-9bf242213fd1b01c, us-code-25-4228-3dea43be040239c7`
  evidence: `{"family_margin": -0.999972491655, "hint_id": "modal-synthesis-75b2d6e2fc31b651", "predicted_family": "temporal", "priority": 1.149972491655, "sample_id": "us-code-34-10153-56c96555be0f0204", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.994348324902, "hint_id": "modal-synthesis-adb81af27f81d919", "predicted_family": "frame", "priority": 1.144348324902, "sample_id": "us-code-48-1668.-9bf242213fd1b01c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.464529535773, "hint_id": "modal-synthesis-e8a3573dd5f642c3", "predicted_family": "conditional_normative", "priority": 0.614529535773, "sample_id": "us-code-25-4228-3dea43be040239c7", "target_family": "temporal"}`
- `program-c6ae9bd6d61f82b0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","deontic->frame","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `0.937067`
  loss: `autoencoder_residual_cluster` = `0.521170379939`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-300x-68c9c55c8a163c4d, us-code-25-181-b1aaf50455600eea, us-code-16-450rr-5e94cfe81f6a5af1, us-code-18-3101-b020ea24c0c5ac85`
  evidence: `{"family_margin": -0.411885467434, "hint_id": "modal-synthesis-024999fe84b1e793", "predicted_family": "temporal", "priority": 0.561885467434, "sample_id": "us-code-25-181-b1aaf50455600eea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-066d93ff31d5a28f", "predicted_family": "frame", "priority": 0.38602129703, "sample_id": "us-code-18-3101-b020ea24c0c5ac85", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-41174f0f9c4ff7c7", "predicted_family": "conditional_normative", "priority": 0.39602509287, "sample_id": "us-code-16-450rr-5e94cfe81f6a5af1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.590749662423, "hint_id": "modal-synthesis-b2ae23fec30bb8f6", "predicted_family": "deontic", "priority": 0.740749662423, "sample_id": "us-code-42-300x-68c9c55c8a163c4d", "target_family": "frame"}`
