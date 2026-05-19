# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-022a48c93b2ff1d1`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.840984786362`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-524-445e0313d6f19fea, us-code-22-2291n-ac54fa9d2b9461be, us-code-12-4105-36d07b104cbb3372`
  evidence: `{"family_margin": -0.073728924867, "hint_id": "modal-synthesis-2acb676239b682e6", "predicted_family": "conditional_normative", "priority": 0.223728924867, "sample_id": "us-code-12-4105-36d07b104cbb3372", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-87d2c49b51e92612", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-28-524-445e0313d6f19fea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.99922543422, "hint_id": "modal-synthesis-e6c6a75858c518e3", "predicted_family": "frame", "priority": 1.14922543422, "sample_id": "us-code-22-2291n-ac54fa9d2b9461be", "target_family": "deontic"}`
- `program-8bbe16b562fd602e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `0.967268`
  loss: `autoencoder_residual_cluster` = `0.612149285211`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1441a-1-044eb239d7ffd95b, us-code-45-921.-904bab83295f76d1, us-code-22-1643m-5242bf8f9ab76629, us-code-21-353d-77f856460111b7bd`
  evidence: `{"family_margin": -0.38106983356, "hint_id": "modal-synthesis-39ac695f1a33ed73", "predicted_family": "deontic", "priority": 0.53106983356, "sample_id": "us-code-22-1643m-5242bf8f9ab76629", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.048490599997, "hint_id": "modal-synthesis-3fabd490c9a0b2ff", "predicted_family": "deontic", "priority": 0.198490599997, "sample_id": "us-code-21-353d-77f856460111b7bd", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.419042466181, "hint_id": "modal-synthesis-63ff7d1fbe8a17cd", "predicted_family": "conditional_normative", "priority": 0.569042466181, "sample_id": "us-code-45-921.-904bab83295f76d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999994241105, "hint_id": "modal-synthesis-ffb012359ac5250b", "predicted_family": "frame", "priority": 1.149994241105, "sample_id": "us-code-12-1441a-1-044eb239d7ffd95b", "target_family": "conditional_normative"}`
