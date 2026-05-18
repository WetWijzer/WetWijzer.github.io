# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-5f869039050eceaa`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5f869039050eceaa` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.148219727408`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-29-431-5c5f795ae7ad35f1, us-code-6-673-d9b9bb9f63235910`
  evidence: `{"family_margin": -0.996647976269, "hint_id": "modal-synthesis-016fa579451a2680", "predicted_family": "deontic", "priority": 1.146647976269, "sample_id": "us-code-6-673-d9b9bb9f63235910", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999791478547, "hint_id": "modal-synthesis-61af7adb59bf9f06", "predicted_family": "deontic", "priority": 1.149791478547, "sample_id": "us-code-29-431-5c5f795ae7ad35f1", "target_family": "temporal"}`
- `program-278272d827487b2e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5f869039050eceaa` score `0.986791`
  loss: `autoencoder_residual_cluster` = `0.874332991004`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-7754-8207fa7435ece575, us-code-16-460nnn-42-c11df48f7209b7aa`
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-8e03e558605021d7", "predicted_family": "frame", "priority": 0.885177285536, "sample_id": "us-code-7-7754-8207fa7435ece575", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.713488696472, "hint_id": "modal-synthesis-942cefa8873aa4f8", "predicted_family": "frame", "priority": 0.863488696472, "sample_id": "us-code-16-460nnn-42-c11df48f7209b7aa", "target_family": "temporal"}`
- `program-4d21c8343a1221c7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5f869039050eceaa` score `0.983742`
  loss: `autoencoder_residual_cluster` = `1.023304327119`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-44307.-afc1426bffbab587, us-code-2-130-b8497891c0fc291f`
  evidence: `{"family_margin": -0.978005248108, "hint_id": "modal-synthesis-2b21d8368a12196f", "predicted_family": "deontic", "priority": 1.128005248108, "sample_id": "us-code-49-44307.-afc1426bffbab587", "target_family": "frame"}`
  evidence: `{"family_margin": -0.76860340613, "hint_id": "modal-synthesis-b124498472faa086", "predicted_family": "frame", "priority": 0.91860340613, "sample_id": "us-code-2-130-b8497891c0fc291f", "target_family": "deontic"}`
- `program-dba2b9aa93ff41a5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5f869039050eceaa` score `0.982657`
  loss: `autoencoder_residual_cluster` = `0.633034076812`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-950aaa-1-14c55da526a5117d, us-code-26-9708-1da9fd91526bb6ee`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-0f590822fc8919f3", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-26-9708-1da9fd91526bb6ee", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.966068153625, "hint_id": "modal-synthesis-eae2a92bc863fe28", "predicted_family": "frame", "priority": 1.116068153625, "sample_id": "us-code-7-950aaa-1-14c55da526a5117d", "target_family": "temporal"}`
- `program-0ff7df44c58eb0f6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5f869039050eceaa` score `0.972634`
  loss: `autoencoder_residual_cluster` = `1.015563945648`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-11-547-3b0ef95c5c121efe, us-code-42-1962d-33b9d57c0aa1c276, us-code-10-10150-2a9db6648ccf9ea4`
  evidence: `{"family_margin": -0.598352142461, "hint_id": "modal-synthesis-77d738fedca55223", "predicted_family": "frame", "priority": 0.748352142461, "sample_id": "us-code-10-10150-2a9db6648ccf9ea4", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999995479351, "hint_id": "modal-synthesis-80279702eb51d852", "predicted_family": "conditional_normative", "priority": 1.149995479351, "sample_id": "us-code-11-547-3b0ef95c5c121efe", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.998344215132, "hint_id": "modal-synthesis-9df6790929c87b00", "predicted_family": "frame", "priority": 1.148344215132, "sample_id": "us-code-42-1962d-33b9d57c0aa1c276", "target_family": "deontic"}`
