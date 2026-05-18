# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-6312ea7c10f8a7fd`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6312ea7c10f8a7fd` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.142890931209`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-2279aa-12-6103b4d4f97c909c, us-code-13-225-022d88a7ec737cff`
  evidence: `{"family_margin": -0.98579105986, "hint_id": "modal-synthesis-6998d22f36bdc30a", "predicted_family": "deontic", "priority": 1.13579105986, "sample_id": "us-code-13-225-022d88a7ec737cff", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999990802558, "hint_id": "modal-synthesis-962890218325b9db", "predicted_family": "deontic", "priority": 1.149990802558, "sample_id": "us-code-12-2279aa-12-6103b4d4f97c909c", "target_family": "temporal"}`
- `program-3a4949f30383fdeb`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6312ea7c10f8a7fd` score `0.977969`
  loss: `autoencoder_residual_cluster` = `0.393710102896`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-43-390tt.-8de8c6b59f628b26, us-code-16-3508-2bf4e0c7753f16bf`
  evidence: `{"family_margin": -0.487420205792, "hint_id": "modal-synthesis-2e6f95437f1d0ce0", "predicted_family": "frame", "priority": 0.637420205792, "sample_id": "us-code-43-390tt.-8de8c6b59f628b26", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-654390c05207cbda", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-3508-2bf4e0c7753f16bf", "target_family": "conditional_normative"}`
- `program-f3be929f7fb47e65`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6312ea7c10f8a7fd` score `0.969528`
  loss: `autoencoder_residual_cluster` = `0.879680739972`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-45101.-251795383fdfac00, us-code-20-1405-b4c7124abd929317, us-code-14-3749-1c344f434d715707`
  evidence: `{"family_margin": -0.966068153625, "hint_id": "modal-synthesis-3b0df695f43762a8", "predicted_family": "frame", "priority": 1.116068153625, "sample_id": "us-code-49-45101.-251795383fdfac00", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.798017084984, "hint_id": "modal-synthesis-a8a8c7cf21690539", "predicted_family": "frame", "priority": 0.948017084984, "sample_id": "us-code-20-1405-b4c7124abd929317", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.424956981306, "hint_id": "modal-synthesis-f8b308771b70107a", "predicted_family": "deontic", "priority": 0.574956981306, "sample_id": "us-code-14-3749-1c344f434d715707", "target_family": "temporal"}`
- `program-919540dd848813bc`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6312ea7c10f8a7fd` score `0.964531`
  loss: `autoencoder_residual_cluster` = `0.742674120065`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-290aa-78672295385145a2, us-code-33-1473-42801b64a1a4742c, us-code-26-3241-51490ac6cfd08db1`
  evidence: `{"family_margin": -0.644460457227, "hint_id": "modal-synthesis-7d5862a3fa0a97cf", "predicted_family": "frame", "priority": 0.794460457227, "sample_id": "us-code-33-1473-42801b64a1a4742c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.349808843776, "hint_id": "modal-synthesis-b94b7be2262e0923", "predicted_family": "temporal", "priority": 0.499808843776, "sample_id": "us-code-26-3241-51490ac6cfd08db1", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.783753059191, "hint_id": "modal-synthesis-c1b7d1c8e1b729da", "predicted_family": "frame", "priority": 0.933753059191, "sample_id": "us-code-42-290aa-78672295385145a2", "target_family": "temporal"}`
- `program-ba4822f5018c4434`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6312ea7c10f8a7fd` score `0.959895`
  loss: `autoencoder_residual_cluster` = `0.733412790273`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-28503.-c10e3b423a6bc14a, us-code-22-5073-afa60918d81318f3, us-code-36-505-bde95a84c02de97c`
  evidence: `{"family_margin": -0.543678283379, "hint_id": "modal-synthesis-dad072595c6fc655", "predicted_family": "deontic", "priority": 0.693678283379, "sample_id": "us-code-22-5073-afa60918d81318f3", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-ecef9e6648776c45", "predicted_family": "frame", "priority": 0.359117456717, "sample_id": "us-code-36-505-bde95a84c02de97c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997442630722, "hint_id": "modal-synthesis-fdf83faf06b18090", "predicted_family": "frame", "priority": 1.147442630722, "sample_id": "us-code-49-28503.-c10e3b423a6bc14a", "target_family": "conditional_normative"}`
