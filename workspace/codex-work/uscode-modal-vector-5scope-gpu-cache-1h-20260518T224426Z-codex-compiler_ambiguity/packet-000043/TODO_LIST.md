# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-127e304a6bdf42ac`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-127e304a6bdf42ac` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.138628439682`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-5207-97035bc3bbe5872e, us-code-25-2402-d2b0b613bb62b381, us-code-5-8338-8843bfb9fff586e8`
  evidence: `{"family_margin": -0.998993452095, "hint_id": "modal-synthesis-0997990ae6c6cb4d", "predicted_family": "frame", "priority": 1.148993452095, "sample_id": "us-code-20-5207-97035bc3bbe5872e", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.982395937648, "hint_id": "modal-synthesis-5387540713eff89b", "predicted_family": "temporal", "priority": 1.132395937648, "sample_id": "us-code-5-8338-8843bfb9fff586e8", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.984495929302, "hint_id": "modal-synthesis-ba36fe1f2805ee35", "predicted_family": "frame", "priority": 1.134495929302, "sample_id": "us-code-25-2402-d2b0b613bb62b381", "target_family": "temporal"}`
- `program-15f265023de594b3`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-127e304a6bdf42ac` score `0.979798`
  loss: `autoencoder_residual_cluster` = `0.75405896186`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-14303-66f5bb7618836ade, us-code-15-1200-5601a302f976a9ea, us-code-46-55335.-66c91ff89c8def29`
  evidence: `{"family_margin": -0.437373806715, "hint_id": "modal-synthesis-207a49f3adcd11dd", "predicted_family": "frame", "priority": 0.587373806715, "sample_id": "us-code-46-55335.-66c91ff89c8def29", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.730342621638, "hint_id": "modal-synthesis-86431f8a23187312", "predicted_family": "temporal", "priority": 0.880342621638, "sample_id": "us-code-10-14303-66f5bb7618836ade", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.644460457227, "hint_id": "modal-synthesis-a51536b474ec70bd", "predicted_family": "frame", "priority": 0.794460457227, "sample_id": "us-code-15-1200-5601a302f976a9ea", "target_family": "deontic"}`
- `program-2fc0e597916fa196`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-127e304a6bdf42ac` score `0.976157`
  loss: `autoencoder_residual_cluster` = `1.026720627325`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-19-4316-0225d3ac8e16aea7, us-code-22-2585-2869b068298ba97c`
  evidence: `{"family_margin": -0.999998131399, "hint_id": "modal-synthesis-091f27a6f618bb06", "predicted_family": "deontic", "priority": 1.149998131399, "sample_id": "us-code-19-4316-0225d3ac8e16aea7", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.753443123251, "hint_id": "modal-synthesis-75424a6d78106be8", "predicted_family": "frame", "priority": 0.903443123251, "sample_id": "us-code-22-2585-2869b068298ba97c", "target_family": "temporal"}`
- `program-d9cb941a10b142c0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-127e304a6bdf42ac` score `0.974684`
  loss: `autoencoder_residual_cluster` = `0.65`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-424-11bcc8f79b455b43, us-code-42-15963.-d6f1ccbcda52e651`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-9346f94c521ec385", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-5-424-11bcc8f79b455b43", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-96fb0777626fe99e", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-42-15963.-d6f1ccbcda52e651", "target_family": "temporal"}`
- `program-96b1e58151939894`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-127e304a6bdf42ac` score `0.965147`
  loss: `autoencoder_residual_cluster` = `0.743852393707`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-20140.-898aa00714233ac7, us-code-10-8864-4ca7313128476150`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-135deb3cef679a79", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-10-8864-4ca7313128476150", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999985294844, "hint_id": "modal-synthesis-e7baec5937a69091", "predicted_family": "deontic", "priority": 1.149985294844, "sample_id": "us-code-49-20140.-898aa00714233ac7", "target_family": "temporal"}`
