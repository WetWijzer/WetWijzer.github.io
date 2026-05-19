# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-238a2cb0f47bc829`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.981456288743`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-30-354-35602e3d70840bd6, us-code-33-1283-61f2dafa7f3bcf77`
  evidence: `{"family_margin": -0.701601171595, "hint_id": "modal-synthesis-9b2ad403a0b81d36", "predicted_family": "deontic", "priority": 0.996298913423, "sample_id": "us-code-30-354-35602e3d70840bd6", "target_family": "temporal", "target_probability": 0.003701086577}`
  evidence: `{"family_margin": -0.709781668325, "hint_id": "modal-synthesis-cb6170e3f7b51e2e", "predicted_family": "frame", "priority": 0.966613664063, "sample_id": "us-code-33-1283-61f2dafa7f3bcf77", "target_family": "temporal", "target_probability": 0.033386335937}`
- `program-df82537458e9c9f5`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `0.974998`
  loss: `autoencoder_residual_cluster` = `0.929451098729`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-47-155.-ae12b5c9c9490b18, us-code-42-1996.-22a4e543fe03ffb6, us-code-16-794-0fe8a57c1c1fd116`
  evidence: `{"family_margin": -0.395294504623, "hint_id": "modal-synthesis-7b5bddb152f79b6c", "predicted_family": "deontic", "priority": 0.91215677675, "sample_id": "us-code-42-1996.-22a4e543fe03ffb6", "target_family": "temporal", "target_probability": 0.08784322325}`
  evidence: `{"family_margin": -0.630382580416, "hint_id": "modal-synthesis-8067808ece228489", "predicted_family": "alethic", "priority": 0.994783679424, "sample_id": "us-code-47-155.-ae12b5c9c9490b18", "target_family": "temporal", "target_probability": 0.005216320576}`
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-c51ac247302f6e25", "predicted_family": "frame", "priority": 0.881412840012, "sample_id": "us-code-16-794-0fe8a57c1c1fd116", "target_family": "deontic", "target_probability": 0.118587159988}`
- `program-1ee6f09f024ff34b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `0.974251`
  loss: `autoencoder_residual_cluster` = `0.862827193214`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-8-1105a-08372dfcfc646b54, us-code-36-110106-99b683bc037f56bc`
  evidence: `{"family_margin": -0.558274622881, "hint_id": "modal-synthesis-991ce2d30ea29bbf", "predicted_family": "frame", "priority": 0.899473461042, "sample_id": "us-code-8-1105a-08372dfcfc646b54", "target_family": "conditional_normative", "target_probability": 0.100526538958}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-b0fe7b1824560c90", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-110106-99b683bc037f56bc", "target_family": "conditional_normative", "target_probability": 0.173819074614}`
- `program-b1cff28e84544a43`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `0.970756`
  loss: `autoencoder_residual_cluster` = `0.698524439009`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-5701-168cf2ab50ae0346, us-code-42-290dd.-2810fb987912153f`
  evidence: `{"family_margin": 0.043571664466, "hint_id": "modal-synthesis-3611114211e60346", "predicted_family": "deontic", "priority": 0.651426684271, "sample_id": "us-code-42-290dd.-2810fb987912153f", "target_family": "deontic", "target_probability": 0.348573315729}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-f0a0b0730ae32019", "predicted_family": "temporal", "priority": 0.745622193746, "sample_id": "us-code-20-5701-168cf2ab50ae0346", "target_family": "deontic", "target_probability": 0.254377806254}`
- `program-1ba96195ab62a678`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `0.949141`
  loss: `autoencoder_residual_cluster` = `0.773447194904`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1856p.-2308d8ca1f73f259, us-code-15-8006-51b18932cd1a4262, us-code-21-21-0631a74417167c39`
  evidence: `{"family_margin": 0.296302829484, "hint_id": "modal-synthesis-7b0109e84ea77e38", "predicted_family": "conditional_normative", "priority": 0.531255825577, "sample_id": "us-code-21-21-0631a74417167c39", "target_family": "conditional_normative", "target_probability": 0.468744174423}`
  evidence: `{"family_margin": -0.466495813484, "hint_id": "modal-synthesis-90992419ffb707ab", "predicted_family": "frame", "priority": 0.795104725875, "sample_id": "us-code-15-8006-51b18932cd1a4262", "target_family": "deontic", "target_probability": 0.204895274125}`
  evidence: `{"family_margin": -0.981223437907, "hint_id": "modal-synthesis-aa1f4217cfc0c0ac", "predicted_family": "frame", "priority": 0.99398103326, "sample_id": "us-code-42-1856p.-2308d8ca1f73f259", "target_family": "conditional_normative", "target_probability": 0.00601896674}`
- `program-576bf052b008ff2e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-238a2cb0f47bc829` score `0.939162`
  loss: `autoencoder_residual_cluster` = `0.873628925052`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1320c-9cb593b2c76aead9, us-code-37-419-bb9c6c1b486640d1, us-code-35-31-0de5c47d579a648d, us-code-7-8105-c1005974f3a24fed`
  evidence: `{"family_margin": -0.907572549173, "hint_id": "modal-synthesis-47b1db611232e0de", "predicted_family": "frame", "priority": 0.992079432595, "sample_id": "us-code-42-1320c-9cb593b2c76aead9", "target_family": "temporal", "target_probability": 0.007920567405}`
  evidence: `{"family_margin": 0.073838799863, "hint_id": "modal-synthesis-9259f6c370e3835d", "predicted_family": "deontic", "priority": 0.593886600754, "sample_id": "us-code-7-8105-c1005974f3a24fed", "target_family": "deontic", "target_probability": 0.406113399246}`
  evidence: `{"family_margin": -0.427971886065, "hint_id": "modal-synthesis-d555b5114079e9d6", "predicted_family": "temporal", "priority": 0.93301484923, "sample_id": "us-code-35-31-0de5c47d579a648d", "target_family": "deontic", "target_probability": 0.06698515077}`
  evidence: `{"family_margin": -0.411364259811, "hint_id": "modal-synthesis-e2e55d3d4be4fd4f", "predicted_family": "frame", "priority": 0.975534817627, "sample_id": "us-code-37-419-bb9c6c1b486640d1", "target_family": "temporal", "target_probability": 0.024465182373}`
