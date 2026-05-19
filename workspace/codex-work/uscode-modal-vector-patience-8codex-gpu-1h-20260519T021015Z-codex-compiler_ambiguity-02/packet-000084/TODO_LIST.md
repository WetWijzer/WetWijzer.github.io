# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-9dae88b284fb8dca`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.804012007245`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-336-fa27971f56c9178b, us-code-25-564u-3e5f6016c5496413`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-90f1302a1008ee78", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-25-564u-3e5f6016c5496413", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-9ec006976f308fef", "predicted_family": "frame", "priority": 0.870554053002, "sample_id": "us-code-18-336-fa27971f56c9178b", "target_family": "deontic"}`
- `program-f63bed7d61012b2a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `0.982101`
  loss: `autoencoder_residual_cluster` = `0.565830299403`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-1035-b286ae25b6800758, us-code-43-25 to 25b.-281e835d4b2de5b0`
  evidence: `{"family_margin": -0.66708163055, "hint_id": "modal-synthesis-6e7d503c63ab0b2b", "predicted_family": "temporal", "priority": 0.81708163055, "sample_id": "us-code-26-1035-b286ae25b6800758", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.164578968256, "hint_id": "modal-synthesis-fdab5eeba1fb0031", "predicted_family": "frame", "priority": 0.314578968256, "sample_id": "us-code-43-25 to 25b.-281e835d4b2de5b0", "target_family": "temporal"}`
- `program-691c6074f6caad2f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `0.980046`
  loss: `autoencoder_residual_cluster` = `0.685702700835`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-40-6306-aeae94d6d1d8eb01, us-code-16-460ss-5-a29152ca8faf3653`
  evidence: `{"family_margin": -0.617808664044, "hint_id": "modal-synthesis-94f5c4d7395853e2", "predicted_family": "deontic", "priority": 0.767808664044, "sample_id": "us-code-40-6306-aeae94d6d1d8eb01", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.453596737625, "hint_id": "modal-synthesis-f1779e058d433f29", "predicted_family": "conditional_normative", "priority": 0.603596737625, "sample_id": "us-code-16-460ss-5-a29152ca8faf3653", "target_family": "deontic"}`
