# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-66b1d86c127d48f9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-66b1d86c127d48f9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.556256638937`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1395w-5efce1b44ff160c2, us-code-42-247b-c7ce522c2799052d`
  evidence: `{"family_margin": -0.812513277874, "hint_id": "modal-synthesis-560c705361af47ae", "predicted_family": "frame", "priority": 0.962513277874, "sample_id": "us-code-42-1395w-5efce1b44ff160c2", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-d22ffeed0f5abd8a", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-42-247b-c7ce522c2799052d", "target_family": "deontic"}`
