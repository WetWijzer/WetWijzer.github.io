# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-1cb7cc02effdbd39`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1cb7cc02effdbd39` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999007743146`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-346a-2-1851abc58a52fa21, us-code-49-20116.-87ead7ff9bdf923b`
  evidence: `{"family_margin": -0.926557636031, "hint_id": "modal-synthesis-0f3f3f1b80bdb703", "predicted_family": "conditional_normative", "priority": 0.998207863341, "sample_id": "us-code-49-20116.-87ead7ff9bdf923b", "target_family": "temporal", "target_probability": 0.001792136659}`
  evidence: `{"family_margin": -0.993772594155, "hint_id": "modal-synthesis-c6a7d0d2a88da6c8", "predicted_family": "frame", "priority": 0.999807622951, "sample_id": "us-code-16-346a-2-1851abc58a52fa21", "target_family": "temporal", "target_probability": 0.000192377049}`
- `program-d7c670baaa4c3b2f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1cb7cc02effdbd39` score `0.974827`
  loss: `autoencoder_residual_cluster` = `0.769754831858`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-49-11501.-5bacf24163dce496, us-code-42-9859.-efaf6c91f0efad0f, us-code-26-5604-65bee4795c1bed4f`
  evidence: `{"family_margin": 0.012950537672, "hint_id": "modal-synthesis-41718aa934f9991d", "predicted_family": "frame", "priority": 0.734460019402, "sample_id": "us-code-42-9859.-efaf6c91f0efad0f", "target_family": "frame", "target_probability": 0.265539980598}`
  evidence: `{"family_margin": -0.148758388224, "hint_id": "modal-synthesis-462fed5974e09b66", "predicted_family": "frame", "priority": 0.574804506839, "sample_id": "us-code-26-5604-65bee4795c1bed4f", "target_family": "deontic", "target_probability": 0.425195493161}`
  evidence: `{"family_margin": -0.999964599906, "hint_id": "modal-synthesis-630f62c8c89f8191", "predicted_family": "frame", "priority": 0.999999969332, "sample_id": "us-code-49-11501.-5bacf24163dce496", "target_family": "temporal", "target_probability": 3.0668e-08}`
- `program-7728d8d6ebf2e48d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1cb7cc02effdbd39` score `0.938283`
  loss: `autoencoder_residual_cluster` = `0.841678334968`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-290n-3-2b067e975d5b088d, us-code-13-3-554d264efed79ab1, us-code-10-909-22586a547806bf91, us-code-42-300a-e57ccd658257dc26`
  evidence: `{"family_margin": -0.40110022983, "hint_id": "modal-synthesis-190904eba52a2650", "predicted_family": "frame", "priority": 0.884797228665, "sample_id": "us-code-10-909-22586a547806bf91", "target_family": "conditional_normative", "target_probability": 0.115202771335}`
  evidence: `{"family_margin": -0.817522388616, "hint_id": "modal-synthesis-916f39f2b4c4c06c", "predicted_family": "frame", "priority": 0.908902856307, "sample_id": "us-code-13-3-554d264efed79ab1", "target_family": "deontic", "target_probability": 0.091097143693}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-c3d52a1a62ac879b", "predicted_family": "frame", "priority": 0.618949048341, "sample_id": "us-code-42-300a-e57ccd658257dc26", "target_family": "conditional_normative", "target_probability": 0.381050951659}`
  evidence: `{"family_margin": -0.876709281778, "hint_id": "modal-synthesis-e0eda994d5b84947", "predicted_family": "deontic", "priority": 0.954064206561, "sample_id": "us-code-22-290n-3-2b067e975d5b088d", "target_family": "temporal", "target_probability": 0.045935793439}`
