# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-023c99d557ac80c7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.018270612789`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-46-55601.-050cf2f773a2a467, us-code-46-14306.-ca967fe82ca4b42b, us-code-7-428-0eedbd792171d56c`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-45ff59380241c15f", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-7-428-0eedbd792171d56c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999627887078, "hint_id": "modal-synthesis-a23482480339b49f", "predicted_family": "frame", "priority": 1.149627887078, "sample_id": "us-code-46-14306.-ca967fe82ca4b42b", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.999999978986, "hint_id": "modal-synthesis-a2423eb9469e3744", "predicted_family": "temporal", "priority": 1.149999978986, "sample_id": "us-code-46-55601.-050cf2f773a2a467", "target_family": "deontic"}`
- `program-8c47a1e614a1d22c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `0.97711`
  loss: `autoencoder_residual_cluster` = `0.624032608238`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-3056.-ca748d473f4cae16, us-code-43-390c.-c8a96ce5a854ea46, us-code-42-7176.-001d470af47d3304`
  evidence: `{"family_margin": -0.42318286485, "hint_id": "modal-synthesis-3e37283620a938af", "predicted_family": "deontic", "priority": 0.57318286485, "sample_id": "us-code-43-390c.-c8a96ce5a854ea46", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-581e5290c951fc60", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-42-7176.-001d470af47d3304", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.998914959864, "hint_id": "modal-synthesis-a73b66292b466b23", "predicted_family": "alethic", "priority": 1.148914959864, "sample_id": "us-code-42-3056.-ca748d473f4cae16", "target_family": "deontic"}`
- `program-366e1942853cf94a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `0.96791`
  loss: `autoencoder_residual_cluster` = `0.949413274649`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-2330b-9aa26e5961270d1d, us-code-16-460aaa-7-9c44309c9a316ae6`
  evidence: `{"family_margin": -0.998961585451, "hint_id": "modal-synthesis-182871496f1fe3fa", "predicted_family": "frame", "priority": 1.148961585451, "sample_id": "us-code-33-2330b-9aa26e5961270d1d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.599864963847, "hint_id": "modal-synthesis-aa58094360529331", "predicted_family": "deontic", "priority": 0.749864963847, "sample_id": "us-code-16-460aaa-7-9c44309c9a316ae6", "target_family": "conditional_normative"}`
