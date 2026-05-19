# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-067e5314efa0aead`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999777991849`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-34-10153-56c96555be0f0204, us-code-25-4228-3dea43be040239c7, us-code-48-1668.-9bf242213fd1b01c`
  evidence: `{"family_margin": -0.464529535773, "hint_id": "modal-synthesis-273ddee65c035623", "predicted_family": "conditional_normative", "priority": 0.99966986857, "sample_id": "us-code-25-4228-3dea43be040239c7", "target_family": "temporal", "target_probability": 0.00033013143}`
  evidence: `{"family_margin": -0.994348324902, "hint_id": "modal-synthesis-2b2f11d4ac212469", "predicted_family": "frame", "priority": 0.999665457364, "sample_id": "us-code-48-1668.-9bf242213fd1b01c", "target_family": "deontic", "target_probability": 0.000334542636}`
  evidence: `{"family_margin": -0.999972491655, "hint_id": "modal-synthesis-7ff66c50fa44d265", "predicted_family": "temporal", "priority": 0.999998649613, "sample_id": "us-code-34-10153-56c96555be0f0204", "target_family": "deontic", "target_probability": 1.350387e-06}`
- `program-393742e51242dfa3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `0.991407`
  loss: `autoencoder_residual_cluster` = `0.812154716605`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-3621-709da9f6e1948604, us-code-10-9772-34f2c9038d0713a9, us-code-16-612-ff406c8a8a0e2154`
  evidence: `{"family_margin": -0.139016052347, "hint_id": "modal-synthesis-115a078c939b9e0b", "predicted_family": "frame", "priority": 0.602650985664, "sample_id": "us-code-16-612-ff406c8a8a0e2154", "target_family": "deontic", "target_probability": 0.397349014336}`
  evidence: `{"family_margin": -0.999999999924, "hint_id": "modal-synthesis-b5491a0e86e1451e", "predicted_family": "temporal", "priority": 0.999999999962, "sample_id": "us-code-18-3621-709da9f6e1948604", "target_family": "conditional_normative", "target_probability": 3.8e-11}`
  evidence: `{"family_margin": -0.285555820105, "hint_id": "modal-synthesis-cde857cc6b575388", "predicted_family": "temporal", "priority": 0.833813164188, "sample_id": "us-code-10-9772-34f2c9038d0713a9", "target_family": "deontic", "target_probability": 0.166186835812}`
- `program-477ecce7df5b7c09`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `0.986929`
  loss: `autoencoder_residual_cluster` = `0.935539672753`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-13-24-c62ea50845a9a459, us-code-50-212.-52c61a0954a48012, us-code-12-4801-6a44921af4549801`
  evidence: `{"family_margin": -0.662709793818, "hint_id": "modal-synthesis-14a91dfeee5ebdca", "predicted_family": "conditional_normative", "priority": 0.996872912541, "sample_id": "us-code-13-24-c62ea50845a9a459", "target_family": "deontic", "target_probability": 0.003127087459}`
  evidence: `{"family_margin": -0.454264517727, "hint_id": "modal-synthesis-a72f299fd51f2590", "predicted_family": "deontic", "priority": 0.928899588501, "sample_id": "us-code-50-212.-52c61a0954a48012", "target_family": "temporal", "target_probability": 0.071100411499}`
  evidence: `{"family_margin": -0.761278285879, "hint_id": "modal-synthesis-d7614b925be6f529", "predicted_family": "temporal", "priority": 0.880846517218, "sample_id": "us-code-12-4801-6a44921af4549801", "target_family": "conditional_normative", "target_probability": 0.119153482782}`
- `program-8db428d76118828b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `0.980456`
  loss: `autoencoder_residual_cluster` = `0.956629511126`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-3456-64343e4f4335b1a1, us-code-15-9034-d76b15a4901912d0`
  evidence: `{"family_margin": -0.384757772757, "hint_id": "modal-synthesis-17e9f9935fcbdca5", "predicted_family": "deontic", "priority": 0.913275723621, "sample_id": "us-code-15-9034-d76b15a4901912d0", "target_family": "temporal", "target_probability": 0.086724276379}`
  evidence: `{"family_margin": -0.999963367228, "hint_id": "modal-synthesis-7930dbdeab3ed3d3", "predicted_family": "conditional_normative", "priority": 0.999983298632, "sample_id": "us-code-10-3456-64343e4f4335b1a1", "target_family": "temporal", "target_probability": 1.6701368e-05}`
- `program-7c95c5e32101680d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `0.97861`
  loss: `autoencoder_residual_cluster` = `0.907920462096`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-2-dup1-64bd7795ee7cbbcc, us-code-22-2271-cad11cc172c48069, us-code-38-3314-2a109138039e1736`
  evidence: `{"family_margin": -0.999999950162, "hint_id": "modal-synthesis-288e0cbebec45a55", "predicted_family": "conditional_normative", "priority": 0.999999999998, "sample_id": "us-code-18-2-dup1-64bd7795ee7cbbcc", "target_family": "frame", "target_probability": 2e-12}`
  evidence: `{"family_margin": -0.567886584382, "hint_id": "modal-synthesis-8df4f905f7dfe295", "predicted_family": "deontic", "priority": 0.858028353905, "sample_id": "us-code-38-3314-2a109138039e1736", "target_family": "conditional_normative", "target_probability": 0.141971646095}`
  evidence: `{"family_margin": -0.358398369222, "hint_id": "modal-synthesis-c7fe72e0a08fbcd5", "predicted_family": "frame", "priority": 0.865733032386, "sample_id": "us-code-22-2271-cad11cc172c48069", "target_family": "epistemic", "target_probability": 0.134266967614}`
- `program-7c2acc553dd00609`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-067e5314efa0aead` score `0.975358`
  loss: `autoencoder_residual_cluster` = `0.993282306404`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-52-10310.-26f34fd94cb731ad, us-code-16-1028-3a1bf3000702288a`
  evidence: `{"family_margin": -0.98344914023, "hint_id": "modal-synthesis-82662d2af498d022", "predicted_family": "frame", "priority": 0.994656256531, "sample_id": "us-code-52-10310.-26f34fd94cb731ad", "target_family": "deontic", "target_probability": 0.005343743469}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-8c7fab99baf34fea", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-16-1028-3a1bf3000702288a", "target_family": "temporal", "target_probability": 0.008091643722}`
