# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-3ae7f382f1326c04`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3ae7f382f1326c04` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.956675746784`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-14042.-0a9611a52b4ee6c7, us-code-50-42.-665c7c7be93a2efb, us-code-16-80d-aff925c919bdb32c`
  evidence: `{"family_margin": -0.717014355684, "hint_id": "modal-synthesis-29eba2b9b825aa69", "predicted_family": "frame", "priority": 0.867014355684, "sample_id": "us-code-16-80d-aff925c919bdb32c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.913314606897, "hint_id": "modal-synthesis-62ee93b031ad6134", "predicted_family": "frame", "priority": 1.063314606897, "sample_id": "us-code-42-14042.-0a9611a52b4ee6c7", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-dd4ea7850abf5537", "predicted_family": "frame", "priority": 0.93969827777, "sample_id": "us-code-50-42.-665c7c7be93a2efb", "target_family": "temporal"}`
- `program-ef35e996efa5eb1a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3ae7f382f1326c04` score `0.974194`
  loss: `autoencoder_residual_cluster` = `0.23305560686`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-16161-05656c7ed7f119d4, us-code-42-7473.-317045e2f473b2e5, us-code-34-10726-675518ae1ebeae48`
  evidence: `{"family_margin": -0.169611967572, "hint_id": "modal-synthesis-08bb0a5777283626", "predicted_family": "frame", "priority": 0.319611967572, "sample_id": "us-code-10-16161-05656c7ed7f119d4", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-5b7ec6200afd53bf", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-34-10726-675518ae1ebeae48", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.079554853007, "hint_id": "modal-synthesis-f540a3d804ffae0b", "predicted_family": "deontic", "priority": 0.229554853007, "sample_id": "us-code-42-7473.-317045e2f473b2e5", "target_family": "conditional_normative"}`
