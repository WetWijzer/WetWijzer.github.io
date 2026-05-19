# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-c152840e2028a6c8`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.954355343565`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-1228c-c9995833bca47965, us-code-5-6120-d6895339c5166af1, us-code-20-3261-ea1591f1a07c9688`
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-8dfb23a2f4b5dc21", "predicted_family": "frame", "priority": 0.676872655614, "sample_id": "us-code-20-3261-ea1591f1a07c9688", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.959954072958, "hint_id": "modal-synthesis-b52c952405055305", "predicted_family": "conditional_normative", "priority": 1.109954072958, "sample_id": "us-code-20-1228c-c9995833bca47965", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.926239302123, "hint_id": "modal-synthesis-e59501dff1215481", "predicted_family": "conditional_normative", "priority": 1.076239302123, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic"}`
- `program-91597b195c6c393d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `0.987232`
  loss: `autoencoder_residual_cluster` = `0.776084199141`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-4801-6a44921af4549801, us-code-13-24-c62ea50845a9a459, us-code-50-212.-52c61a0954a48012`
  evidence: `{"family_margin": -0.761278285879, "hint_id": "modal-synthesis-28b39cc864cb6bd9", "predicted_family": "temporal", "priority": 0.911278285879, "sample_id": "us-code-12-4801-6a44921af4549801", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.662709793818, "hint_id": "modal-synthesis-b9fd093c0cd037f2", "predicted_family": "conditional_normative", "priority": 0.812709793818, "sample_id": "us-code-13-24-c62ea50845a9a459", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.454264517727, "hint_id": "modal-synthesis-ebb303c849ea94b0", "predicted_family": "deontic", "priority": 0.604264517727, "sample_id": "us-code-50-212.-52c61a0954a48012", "target_family": "temporal"}`
- `program-23511494970734d7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `0.973176`
  loss: `autoencoder_residual_cluster` = `0.624857290792`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-3621-709da9f6e1948604, us-code-10-9772-34f2c9038d0713a9, us-code-16-612-ff406c8a8a0e2154`
  evidence: `{"family_margin": -0.999999999924, "hint_id": "modal-synthesis-017154b616ac99e8", "predicted_family": "temporal", "priority": 1.149999999924, "sample_id": "us-code-18-3621-709da9f6e1948604", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.285555820105, "hint_id": "modal-synthesis-29f1bd6104434890", "predicted_family": "temporal", "priority": 0.435555820105, "sample_id": "us-code-10-9772-34f2c9038d0713a9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.139016052347, "hint_id": "modal-synthesis-6116da582d49120d", "predicted_family": "frame", "priority": 0.289016052347, "sample_id": "us-code-16-612-ff406c8a8a0e2154", "target_family": "deontic"}`
