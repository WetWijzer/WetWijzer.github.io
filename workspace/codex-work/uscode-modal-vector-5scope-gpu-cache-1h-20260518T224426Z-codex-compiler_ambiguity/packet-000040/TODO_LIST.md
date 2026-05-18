# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-2c7aaea024460c9c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2c7aaea024460c9c` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.03382276156`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-34-12592-82443ae2f01d717b, us-code-42-17 to 25e.-be36c9c1c5425f87, us-code-22-2430-a7c89ee5fb520213`
  evidence: `{"family_margin": -0.772263349992, "hint_id": "modal-synthesis-57468b1ddee32591", "predicted_family": "frame", "priority": 0.922263349992, "sample_id": "us-code-22-2430-a7c89ee5fb520213", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999987782534, "hint_id": "modal-synthesis-d714e4f04e0c8b66", "predicted_family": "conditional_normative", "priority": 1.149987782534, "sample_id": "us-code-34-12592-82443ae2f01d717b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.879217152154, "hint_id": "modal-synthesis-f02bae96fcaf4cf8", "predicted_family": "temporal", "priority": 1.029217152154, "sample_id": "us-code-42-17 to 25e.-be36c9c1c5425f87", "target_family": "conditional_normative"}`
- `program-da1be72141a172ae`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2c7aaea024460c9c` score `0.973164`
  loss: `autoencoder_residual_cluster` = `1.004078903171`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-48-738.-135a97644c35fe12, us-code-2-2165-f47062f31de4af78, us-code-22-262p-4c-56831f6deff3c8ac`
  evidence: `{"family_margin": -0.644460457227, "hint_id": "modal-synthesis-162aa8b7f1642f7b", "predicted_family": "frame", "priority": 0.794460457227, "sample_id": "us-code-22-262p-4c-56831f6deff3c8ac", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.990601045781, "hint_id": "modal-synthesis-307f83b5d7c31ed1", "predicted_family": "frame", "priority": 1.140601045781, "sample_id": "us-code-48-738.-135a97644c35fe12", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-88093dd519b3fabd", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-2-2165-f47062f31de4af78", "target_family": "temporal"}`
- `program-69e640d4b0ad3328`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2c7aaea024460c9c` score `0.971916`
  loss: `autoencoder_residual_cluster` = `0.803986458263`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-7280-13cee2a3ef546c5d, us-code-22-3501-11ece58c84eb6fdc, us-code-33-3851-90ea8dc99c00b4a9`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-4cbf0c4fe9440103", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-33-3851-90ea8dc99c00b4a9", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.995891221163, "hint_id": "modal-synthesis-83087771704f0d6e", "predicted_family": "frame", "priority": 1.145891221163, "sample_id": "us-code-10-7280-13cee2a3ef546c5d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.966068153625, "hint_id": "modal-synthesis-abbe8cec12311ae2", "predicted_family": "frame", "priority": 1.116068153625, "sample_id": "us-code-22-3501-11ece58c84eb6fdc", "target_family": "temporal"}`
- `program-2285f0cb22d65bf9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","epistemic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2c7aaea024460c9c` score `0.961672`
  loss: `autoencoder_residual_cluster` = `0.774189594765`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-441-10b6a4089d8de64e, us-code-26-114-ccb6bf617a6f040b, us-code-42-300bb-2b88b2e88e183d1f, us-code-33-3035-a7915fcc2f74a46f`
  evidence: `{"family_margin": -0.989029958842, "hint_id": "modal-synthesis-1fe38c45af6af096", "predicted_family": "deontic", "priority": 1.139029958842, "sample_id": "us-code-26-114-ccb6bf617a6f040b", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b158946960bad07c", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-33-3035-a7915fcc2f74a46f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-b9aba30b0c99856b", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-42-300bb-2b88b2e88e183d1f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.989182737833, "hint_id": "modal-synthesis-fc8892018b25ee11", "predicted_family": "deontic", "priority": 1.139182737833, "sample_id": "us-code-22-441-10b6a4089d8de64e", "target_family": "temporal"}`
- `program-1b7d65bb53391744`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2c7aaea024460c9c` score `0.961363`
  loss: `autoencoder_residual_cluster` = `0.923166506492`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-19-1671d-139f3d4588167a39, us-code-42-286c.-f47109acd9f56a01`
  evidence: `{"family_margin": -0.546345385758, "hint_id": "modal-synthesis-622dab1b0d202871", "predicted_family": "deontic", "priority": 0.696345385758, "sample_id": "us-code-42-286c.-f47109acd9f56a01", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999987627225, "hint_id": "modal-synthesis-e0b86232cb12539e", "predicted_family": "frame", "priority": 1.149987627225, "sample_id": "us-code-19-1671d-139f3d4588167a39", "target_family": "temporal"}`
