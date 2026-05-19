# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-a1072139d3ad792c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a1072139d3ad792c` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.016825843913`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-4901-2ad5a8db3570b4d3, us-code-16-460z-8-a67203ffef3c484d`
  evidence: `{"family_margin": -0.99999999986, "hint_id": "modal-synthesis-2f7019ef663d2826", "predicted_family": "temporal", "priority": 1.14999999986, "sample_id": "us-code-10-4901-2ad5a8db3570b4d3", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.733651687966, "hint_id": "modal-synthesis-33f438d51559141e", "predicted_family": "conditional_normative", "priority": 0.883651687966, "sample_id": "us-code-16-460z-8-a67203ffef3c484d", "target_family": "temporal"}`
- `program-e65e043374a5b48d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a1072139d3ad792c` score `0.946631`
  loss: `autoencoder_residual_cluster` = `0.666096771966`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-6-609a-150079c952e10074, us-code-42-3030s-33be9732cb2dba7c, us-code-2-2186-d4e6d688fb2a82ea, us-code-14-2742-456f60f74aa67e0b`
  evidence: `{"family_margin": -0.472985425568, "hint_id": "modal-synthesis-06d802e2caaaefe4", "predicted_family": "frame", "priority": 0.622985425568, "sample_id": "us-code-2-2186-d4e6d688fb2a82ea", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.750196392965, "hint_id": "modal-synthesis-5a6d48db95fa8876", "predicted_family": "temporal", "priority": 0.900196392965, "sample_id": "us-code-6-609a-150079c952e10074", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-6f7d13cb1d913547", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-42-3030s-33be9732cb2dba7c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-ad289818dcded7b4", "predicted_family": "frame", "priority": 0.38602129703, "sample_id": "us-code-14-2742-456f60f74aa67e0b", "target_family": "deontic"}`
- `program-e6fa4cf12901293f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a1072139d3ad792c` score `0.931328`
  loss: `autoencoder_residual_cluster` = `0.601495486471`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-631-6e11e9c04c478164, us-code-31-9304-36b77881bd08ed11, us-code-12-2279bb-4-c0cf7ff71e262f12, us-code-16-1102-773d6f6af055aefe`
  evidence: `{"family_margin": -0.672350770204, "hint_id": "modal-synthesis-330a5fd736e9adb9", "predicted_family": "deontic", "priority": 0.822350770204, "sample_id": "us-code-31-9304-36b77881bd08ed11", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b3142a6d24e32e57", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-1102-773d6f6af055aefe", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.989531255351, "hint_id": "modal-synthesis-c6734c138f96c8b8", "predicted_family": "frame", "priority": 1.139531255351, "sample_id": "us-code-33-631-6e11e9c04c478164", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.144099920331, "hint_id": "modal-synthesis-dfe4af977650ccd0", "predicted_family": "conditional_normative", "priority": 0.294099920331, "sample_id": "us-code-12-2279bb-4-c0cf7ff71e262f12", "target_family": "deontic"}`
