# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-b190fd7a25bf7b26`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->dynamic","frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b190fd7a25bf7b26` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.931854300064`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-6339-2bc797bee283b898, us-code-20-80e-6f0a800587a2c144, us-code-16-450cc-1-ea8ceb5d23d67cf1, us-code-20-192-5ed09069c63138ac`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-5c8d7708712e0f63", "predicted_family": "frame", "priority": 0.870554053002, "sample_id": "us-code-16-450cc-1-ea8ceb5d23d67cf1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.804383280095, "hint_id": "modal-synthesis-bbb86141017e9f1d", "predicted_family": "frame", "priority": 0.954383280095, "sample_id": "us-code-20-80e-6f0a800587a2c144", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-ec6e75aca0874df4", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-20-192-5ed09069c63138ac", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997295894855, "hint_id": "modal-synthesis-f5f18e622b03dbec", "predicted_family": "deontic", "priority": 1.147295894855, "sample_id": "us-code-5-6339-2bc797bee283b898", "target_family": "dynamic"}`
