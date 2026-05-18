# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-0f3619466d6d0393`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0f3619466d6d0393` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.39366573559`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-59-693f71484c6a9a7a, us-code-46-30525.-99a6422ab828fa0c, us-code-48-1422b.-1024d577005506f9`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-089fc5b98e73c642", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-46-30525.-99a6422ab828fa0c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-100a09f68f736c4b", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-48-1422b.-1024d577005506f9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.730997206769, "hint_id": "modal-synthesis-b11365529676c1b4", "predicted_family": "temporal", "priority": 0.880997206769, "sample_id": "us-code-12-59-693f71484c6a9a7a", "target_family": "conditional_normative"}`
