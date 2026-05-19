# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-8e0f409a15b3d32f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8e0f409a15b3d32f` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.964519724684`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-77x-1c3697f7e522de6d, us-code-42-1456 to 1460.-1230df83a3d48e0f, us-code-7-368-b209040cf84318cf`
  evidence: `{"family_margin": -0.993083986751, "hint_id": "modal-synthesis-0b7f1805456491ac", "predicted_family": "frame", "priority": 1.143083986751, "sample_id": "us-code-15-77x-1c3697f7e522de6d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.923602531686, "hint_id": "modal-synthesis-8f073115dc18656a", "predicted_family": "frame", "priority": 1.073602531686, "sample_id": "us-code-42-1456 to 1460.-1230df83a3d48e0f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-d0cecc7c2a15bd62", "predicted_family": "frame", "priority": 0.676872655614, "sample_id": "us-code-7-368-b209040cf84318cf", "target_family": "temporal"}`
- `program-afcc6e0b2b2c06b0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8e0f409a15b3d32f` score `0.979745`
  loss: `autoencoder_residual_cluster` = `0.843601103932`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1975-9de95ba2da51c9bc, us-code-26-224-4cbc6b9203a4f7a2`
  evidence: `{"family_margin": -0.874623237248, "hint_id": "modal-synthesis-0c3368e7e96029f9", "predicted_family": "deontic", "priority": 1.024623237248, "sample_id": "us-code-12-1975-9de95ba2da51c9bc", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.512578970616, "hint_id": "modal-synthesis-d72cf407d4d3077e", "predicted_family": "frame", "priority": 0.662578970616, "sample_id": "us-code-26-224-4cbc6b9203a4f7a2", "target_family": "conditional_normative"}`
- `program-b9f9fb412bfaf8b7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8e0f409a15b3d32f` score `0.972821`
  loss: `autoencoder_residual_cluster` = `0.85569141996`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-1283-61f2dafa7f3bcf77, us-code-30-354-35602e3d70840bd6`
  evidence: `{"family_margin": -0.709781668325, "hint_id": "modal-synthesis-1ac924bc144a5349", "predicted_family": "frame", "priority": 0.859781668325, "sample_id": "us-code-33-1283-61f2dafa7f3bcf77", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.701601171595, "hint_id": "modal-synthesis-43a786c1d8d50dc2", "predicted_family": "deontic", "priority": 0.851601171595, "sample_id": "us-code-30-354-35602e3d70840bd6", "target_family": "temporal"}`
- `program-ad08e82ac21233f7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8e0f409a15b3d32f` score `0.955299`
  loss: `autoencoder_residual_cluster` = `0.629713556121`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-294-a171a8719480b66f, us-code-18-3608-3f5a1a151ad167fc, us-code-38-1115-6aa7ee0ac263a2cc, us-code-42-12146.-4c26f8dff8d901ea`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2798a757b9b3c6b1", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-42-12146.-4c26f8dff8d901ea", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.462986986964, "hint_id": "modal-synthesis-588d532b3077e889", "predicted_family": "temporal", "priority": 0.612986986964, "sample_id": "us-code-38-1115-6aa7ee0ac263a2cc", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.955002039866, "hint_id": "modal-synthesis-67425ca23922eaa5", "predicted_family": "frame", "priority": 1.105002039866, "sample_id": "us-code-28-294-a171a8719480b66f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.500865197654, "hint_id": "modal-synthesis-769718b5bacf672e", "predicted_family": "frame", "priority": 0.650865197654, "sample_id": "us-code-18-3608-3f5a1a151ad167fc", "target_family": "deontic"}`
