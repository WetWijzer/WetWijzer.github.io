# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-496021e102ba8377`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-496021e102ba8377` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.942536607759`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-76h-1f1ce11e05701c8d, us-code-42-7605.-4569102489e5c30e, us-code-22-10012-9becbd88b9c27185`
  evidence: `{"family_margin": -0.481653071989, "hint_id": "modal-synthesis-8e269b3d27b3e62a", "predicted_family": "frame", "priority": 0.631653071989, "sample_id": "us-code-22-10012-9becbd88b9c27185", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.932971796823, "hint_id": "modal-synthesis-be4c95a111267598", "predicted_family": "frame", "priority": 1.082971796823, "sample_id": "us-code-42-7605.-4569102489e5c30e", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.962984954465, "hint_id": "modal-synthesis-e1851da794b7423c", "predicted_family": "alethic", "priority": 1.112984954465, "sample_id": "us-code-20-76h-1f1ce11e05701c8d", "target_family": "deontic"}`
- `program-d0b8eb399f28e674`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->frame","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-496021e102ba8377` score `0.97974`
  loss: `autoencoder_residual_cluster` = `0.730931764464`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-33104.-ca32bd54a404f9ed, us-code-20-1097a-38d407570ced3346, us-code-16-799-ed4b744b4bed77ee`
  evidence: `{"family_margin": -0.65648643313, "hint_id": "modal-synthesis-1a10dab4e63b55ce", "predicted_family": "deontic", "priority": 0.80648643313, "sample_id": "us-code-20-1097a-38d407570ced3346", "target_family": "frame"}`
  evidence: `{"family_margin": -0.800565026919, "hint_id": "modal-synthesis-2ea04f7698b79ba7", "predicted_family": "frame", "priority": 0.950565026919, "sample_id": "us-code-49-33104.-ca32bd54a404f9ed", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.285743833344, "hint_id": "modal-synthesis-8901212ff4676805", "predicted_family": "alethic", "priority": 0.435743833344, "sample_id": "us-code-16-799-ed4b744b4bed77ee", "target_family": "deontic"}`
- `program-94cea4d8667b25f7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-496021e102ba8377` score `0.969801`
  loss: `autoencoder_residual_cluster` = `0.396335565319`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-50-47c.-dad134a96a1b873e, us-code-16-460uu-43-fb997cc1fd28fc71, us-code-10-9414b-072e75b5332bc57b`
  evidence: `{"family_margin": -0.731688096648, "hint_id": "modal-synthesis-319da317fcbad7f2", "predicted_family": "frame", "priority": 0.881688096648, "sample_id": "us-code-50-47c.-dad134a96a1b873e", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.128767093112, "hint_id": "modal-synthesis-cecdde6d4ccebab0", "predicted_family": "deontic", "priority": 0.021232906888, "sample_id": "us-code-10-9414b-072e75b5332bc57b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.136085692421, "hint_id": "modal-synthesis-ff606f07f77fa191", "predicted_family": "deontic", "priority": 0.286085692421, "sample_id": "us-code-16-460uu-43-fb997cc1fd28fc71", "target_family": "conditional_normative"}`
- `program-90b528d52719a638`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-496021e102ba8377` score `0.965438`
  loss: `autoencoder_residual_cluster` = `0.664656617323`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-1-113-cd403ab39cd45f1c, us-code-12-338-e9f61eb9e13a678a, us-code-22-801-5e460b92fcea13cc, us-code-22-7707-cdc74b8d1b080e59`
  evidence: `{"family_margin": -0.046351027126, "hint_id": "modal-synthesis-285e5d671675f3dc", "predicted_family": "deontic", "priority": 0.196351027126, "sample_id": "us-code-22-7707-cdc74b8d1b080e59", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999373752102, "hint_id": "modal-synthesis-808fd574beb17453", "predicted_family": "frame", "priority": 1.149373752102, "sample_id": "us-code-1-113-cd403ab39cd45f1c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.447743270967, "hint_id": "modal-synthesis-d5a2bfdba6cea208", "predicted_family": "conditional_normative", "priority": 0.597743270967, "sample_id": "us-code-22-801-5e460b92fcea13cc", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.565158419096, "hint_id": "modal-synthesis-f311455ecfaa561a", "predicted_family": "deontic", "priority": 0.715158419096, "sample_id": "us-code-12-338-e9f61eb9e13a678a", "target_family": "temporal"}`
- `program-2a0fc8ffd0d20211`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-496021e102ba8377` score `0.955776`
  loss: `autoencoder_residual_cluster` = `0.869796281549`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-78eee-47692ccfd3495db1, us-code-10-2733-ebd64ecca90fe68f, us-code-49-44740.-385deadf37a5de7e, us-code-29-1102-1f26b22c27201dac`
  evidence: `{"family_margin": -0.985536140844, "hint_id": "modal-synthesis-c4a37ca98cb382f2", "predicted_family": "frame", "priority": 1.135536140844, "sample_id": "us-code-10-2733-ebd64ecca90fe68f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.089539783655, "hint_id": "modal-synthesis-ca773d1ce492a887", "predicted_family": "deontic", "priority": 0.060460216345, "sample_id": "us-code-29-1102-1f26b22c27201dac", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999999367585, "hint_id": "modal-synthesis-d6d0106c6dc2b001", "predicted_family": "frame", "priority": 1.149999367585, "sample_id": "us-code-15-78eee-47692ccfd3495db1", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.983189401423, "hint_id": "modal-synthesis-f9784c20ddd3ed18", "predicted_family": "frame", "priority": 1.133189401423, "sample_id": "us-code-49-44740.-385deadf37a5de7e", "target_family": "deontic"}`
