# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-129dc3175bc5220e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-129dc3175bc5220e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.998687131085`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-2603-bcfd65caaa9561e6, us-code-26-3503-c8327a9a01871766`
  evidence: `{"family_margin": -0.998666367346, "hint_id": "modal-synthesis-8cc26bf6e1cd0a34", "predicted_family": "frame", "priority": 0.999556534506, "sample_id": "us-code-16-2603-bcfd65caaa9561e6", "target_family": "temporal", "target_probability": 0.000443465494}`
  evidence: `{"family_margin": -0.829552719341, "hint_id": "modal-synthesis-af79a9bc88ccce0a", "predicted_family": "conditional_normative", "priority": 0.997817727664, "sample_id": "us-code-26-3503-c8327a9a01871766", "target_family": "temporal", "target_probability": 0.002182272336}`
- `program-af8af13726969a14`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-129dc3175bc5220e` score `0.992023`
  loss: `autoencoder_residual_cluster` = `0.824375542821`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-414.-2a783382bd72bea8, us-code-42-10200.-91ec933481f4ed65`
  evidence: `{"family_margin": -0.999705086765, "hint_id": "modal-synthesis-a64e235c697a4654", "predicted_family": "frame", "priority": 0.999894526912, "sample_id": "us-code-42-414.-2a783382bd72bea8", "target_family": "conditional_normative", "target_probability": 0.000105473088}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-f03e5df142003cf6", "predicted_family": "temporal", "priority": 0.64885655873, "sample_id": "us-code-42-10200.-91ec933481f4ed65", "target_family": "temporal", "target_probability": 0.35114344127}`
- `program-f26d732d1f00850a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-129dc3175bc5220e` score `0.968454`
  loss: `autoencoder_residual_cluster` = `0.898859093151`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-3505c.-45b35f1c498964b6, us-code-40-5103-46b4843dca9dca6b, us-code-10-8896-be9d438fb8cac68a`
  evidence: `{"family_margin": -0.640998164291, "hint_id": "modal-synthesis-5d0d28e580db9252", "predicted_family": "temporal", "priority": 0.953477068913, "sample_id": "us-code-42-3505c.-45b35f1c498964b6", "target_family": "deontic", "target_probability": 0.046522931087}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-5d694c8164aac2f4", "predicted_family": "frame", "priority": 0.943149448469, "sample_id": "us-code-40-5103-46b4843dca9dca6b", "target_family": "temporal", "target_probability": 0.056850551531}`
  evidence: `{"family_margin": -0.236958646552, "hint_id": "modal-synthesis-fdb6f5a5a8b698a9", "predicted_family": "frame", "priority": 0.799950762071, "sample_id": "us-code-10-8896-be9d438fb8cac68a", "target_family": "temporal", "target_probability": 0.200049237929}`
- `program-5c2200611414f68a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-129dc3175bc5220e` score `0.951204`
  loss: `autoencoder_residual_cluster` = `0.956438458931`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-971d-8be9f90451757eeb, us-code-25-1522-a7af7b78aeccf308, us-code-42-7546.-f2898bded36e826a`
  evidence: `{"family_margin": -0.99872993958, "hint_id": "modal-synthesis-2a67ac0bd042568b", "predicted_family": "alethic", "priority": 0.999986251689, "sample_id": "us-code-16-971d-8be9f90451757eeb", "target_family": "deontic", "target_probability": 1.3748311e-05}`
  evidence: `{"family_margin": -0.391262453299, "hint_id": "modal-synthesis-2acd220c50a05f32", "predicted_family": "deontic", "priority": 0.945315038026, "sample_id": "us-code-25-1522-a7af7b78aeccf308", "target_family": "conditional_normative", "target_probability": 0.054684961974}`
  evidence: `{"family_margin": -0.819471463415, "hint_id": "modal-synthesis-f1c0270fe322fca7", "predicted_family": "frame", "priority": 0.924014087078, "sample_id": "us-code-42-7546.-f2898bded36e826a", "target_family": "deontic", "target_probability": 0.075985912922}`
