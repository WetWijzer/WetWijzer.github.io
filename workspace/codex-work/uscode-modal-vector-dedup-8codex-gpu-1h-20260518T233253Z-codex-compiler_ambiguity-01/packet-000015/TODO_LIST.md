# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4870701f382931b2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4870701f382931b2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.802553816863`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-5422.-5b961f79f3664b3e, us-code-34-21301-1e886420be029827, us-code-49-60127.-8664408f5c716452`
  evidence: `{"family_margin": -0.999091663546, "hint_id": "modal-synthesis-6e8aa7add01e4a84", "predicted_family": "deontic", "priority": 1.149091663546, "sample_id": "us-code-42-5422.-5b961f79f3664b3e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.71376499545, "hint_id": "modal-synthesis-9b1534a5e529dbbe", "predicted_family": "frame", "priority": 0.86376499545, "sample_id": "us-code-34-21301-1e886420be029827", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.244804791593, "hint_id": "modal-synthesis-d2a865975a9fceed", "predicted_family": "frame", "priority": 0.394804791593, "sample_id": "us-code-49-60127.-8664408f5c716452", "target_family": "deontic"}`
