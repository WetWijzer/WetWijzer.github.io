# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-ec8121fe8a2b5fc9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ec8121fe8a2b5fc9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.816524617836`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-3305-53aaebf91aa3d889, us-code-38-8163-dc4c9191b09f4a3d, us-code-10-649j-49b85ae09715be03`
  evidence: `{"family_margin": -0.999664649245, "hint_id": "modal-synthesis-0345bdeb73aa5f4b", "predicted_family": "deontic", "priority": 1.149664649245, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-4641802220f5f009", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-10-649j-49b85ae09715be03", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999909204262, "hint_id": "modal-synthesis-4b41db6e3f49d0e5", "predicted_family": "temporal", "priority": 1.149909204262, "sample_id": "us-code-26-3305-53aaebf91aa3d889", "target_family": "deontic"}`
