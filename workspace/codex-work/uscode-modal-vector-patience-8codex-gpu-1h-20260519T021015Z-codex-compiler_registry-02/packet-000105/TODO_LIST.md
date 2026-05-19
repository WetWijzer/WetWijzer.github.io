# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-13021a336ad404de`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-13021a336ad404de` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.968187948004`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-5370-7a08b2959e7f0721, us-code-12-4145-29f1b6e849d52610, us-code-10-1207-3747e5081e568c1e`
  evidence: `{"family_margin": -0.989479571796, "hint_id": "modal-synthesis-5f8cbd119c78da74", "predicted_family": "conditional_normative", "priority": 0.994995817998, "sample_id": "us-code-12-4145-29f1b6e849d52610", "target_family": "deontic", "target_probability": 0.005004182002}`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-723ef35173bdc367", "predicted_family": "frame", "priority": 0.912003318214, "sample_id": "us-code-10-1207-3747e5081e568c1e", "target_family": "deontic", "target_probability": 0.087996681786}`
  evidence: `{"family_margin": -0.839730500363, "hint_id": "modal-synthesis-d2f374a3d0cdd960", "predicted_family": "deontic", "priority": 0.997564707801, "sample_id": "us-code-12-5370-7a08b2959e7f0721", "target_family": "frame", "target_probability": 0.002435292199}`
- `program-cc0e77f09c844d72`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-13021a336ad404de` score `0.979015`
  loss: `autoencoder_residual_cluster` = `0.938639936839`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1104.-e394bd5517bbd020, us-code-38-3678-3d85bc7a52705388, us-code-43-373d.-735b38078b23dd60`
  evidence: `{"family_margin": -0.487420205792, "hint_id": "modal-synthesis-5baa0595751eb587", "predicted_family": "frame", "priority": 0.817397514594, "sample_id": "us-code-43-373d.-735b38078b23dd60", "target_family": "temporal", "target_probability": 0.182602485406}`
  evidence: `{"family_margin": -0.980421678302, "hint_id": "modal-synthesis-c5e7872d87ff7ddc", "predicted_family": "frame", "priority": 0.99852377621, "sample_id": "us-code-38-3678-3d85bc7a52705388", "target_family": "conditional_normative", "target_probability": 0.00147622379}`
  evidence: `{"family_margin": -0.993227253513, "hint_id": "modal-synthesis-db9b10528524f468", "predicted_family": "conditional_normative", "priority": 0.999998519714, "sample_id": "us-code-42-1104.-e394bd5517bbd020", "target_family": "deontic", "target_probability": 1.480286e-06}`
- `program-5564384a886a249a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-13021a336ad404de` score `0.976486`
  loss: `autoencoder_residual_cluster` = `0.927268645552`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-366-83baa05ec62b679e, us-code-36-151711-f16ce2b197078b60, us-code-38-7105A-fcf06bab2445fce1, us-code-46-4305.-9d1d567673716470`
  evidence: `{"family_margin": -0.507478180282, "hint_id": "modal-synthesis-017196e9b8d8f6ab", "predicted_family": "alethic", "priority": 0.970451037337, "sample_id": "us-code-16-366-83baa05ec62b679e", "target_family": "frame", "target_probability": 0.029548962663}`
  evidence: `{"family_margin": -0.463831688409, "hint_id": "modal-synthesis-0fbc2614c2bfdcd5", "predicted_family": "frame", "priority": 0.82623449314, "sample_id": "us-code-46-4305.-9d1d567673716470", "target_family": "conditional_normative", "target_probability": 0.17376550686}`
  evidence: `{"family_margin": -0.907898318806, "hint_id": "modal-synthesis-502e765f243e1d1f", "predicted_family": "frame", "priority": 0.957294757499, "sample_id": "us-code-36-151711-f16ce2b197078b60", "target_family": "deontic", "target_probability": 0.042705242501}`
  evidence: `{"family_margin": -0.704783114489, "hint_id": "modal-synthesis-e6d5ce36bb8862ee", "predicted_family": "frame", "priority": 0.955094294233, "sample_id": "us-code-38-7105A-fcf06bab2445fce1", "target_family": "deontic", "target_probability": 0.044905705767}`
- `program-c51622a22d31cb5c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-13021a336ad404de` score `0.973357`
  loss: `autoencoder_residual_cluster` = `0.956198722058`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-4370d.-bb603ed61730713f, us-code-36-30304-0b23c1753243b86c, us-code-5-418-de842a2d8c1aedd4, us-code-22-9532-7da7d6963d8c4f1a`
  evidence: `{"family_margin": -0.511224549803, "hint_id": "modal-synthesis-31d6b4b485e5f4ff", "predicted_family": "temporal", "priority": 0.919984338549, "sample_id": "us-code-22-9532-7da7d6963d8c4f1a", "target_family": "conditional_normative", "target_probability": 0.080015661451}`
  evidence: `{"family_margin": -0.940823512233, "hint_id": "modal-synthesis-3b14599b4bb42c79", "predicted_family": "frame", "priority": 0.975917915513, "sample_id": "us-code-36-30304-0b23c1753243b86c", "target_family": "deontic", "target_probability": 0.024082084487}`
  evidence: `{"family_margin": -0.993652129001, "hint_id": "modal-synthesis-d5a5f5fbe13a1d58", "predicted_family": "frame", "priority": 0.999450122409, "sample_id": "us-code-42-4370d.-bb603ed61730713f", "target_family": "temporal", "target_probability": 0.000549877591}`
  evidence: `{"family_margin": -0.633195772991, "hint_id": "modal-synthesis-e39b87fc2f3859c3", "predicted_family": "frame", "priority": 0.929442511763, "sample_id": "us-code-5-418-de842a2d8c1aedd4", "target_family": "deontic", "target_probability": 0.070557488237}`
- `program-52aba6a4d1add717`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-13021a336ad404de` score `0.956353`
  loss: `autoencoder_residual_cluster` = `0.850601902418`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1490h.-f8a747e85ba922c7, us-code-49-60143.-bbe39953f892dc35`
  evidence: `{"family_margin": -0.357890198984, "hint_id": "modal-synthesis-0710060c1e15d90e", "predicted_family": "deontic", "priority": 0.703555767549, "sample_id": "us-code-49-60143.-bbe39953f892dc35", "target_family": "conditional_normative", "target_probability": 0.296444232451}`
  evidence: `{"family_margin": -0.946497516393, "hint_id": "modal-synthesis-0ea53fcade7d363f", "predicted_family": "conditional_normative", "priority": 0.997648037288, "sample_id": "us-code-42-1490h.-f8a747e85ba922c7", "target_family": "temporal", "target_probability": 0.002351962712}`
