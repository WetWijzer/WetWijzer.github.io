# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-276b6d75376a3fb0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-276b6d75376a3fb0` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.028991445704`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-7310A-219731bd25fca43f, us-code-22-2779a-2f9baaa9ac52eacf, us-code-26-646-0cfbbfe0c86b90ae, us-code-54-101511.-54b6ccb5549961cf`
  evidence: `{"family_margin": -0.904857016623, "hint_id": "modal-synthesis-17eb0cae60f9ae84", "predicted_family": "temporal", "priority": 1.054857016623, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.880797076722, "hint_id": "modal-synthesis-267835c7ca3343dd", "predicted_family": "deontic", "priority": 1.030797076722, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.730558609294, "hint_id": "modal-synthesis-560a535b79ebd3ed", "predicted_family": "temporal", "priority": 0.880558609294, "sample_id": "us-code-54-101511.-54b6ccb5549961cf", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999753080179, "hint_id": "modal-synthesis-9324d6490c631c0a", "predicted_family": "temporal", "priority": 1.149753080179, "sample_id": "us-code-38-7310A-219731bd25fca43f", "target_family": "deontic"}`
