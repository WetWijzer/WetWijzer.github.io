# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-094bfa682f6eb802`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-094bfa682f6eb802` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.9802147206`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-21-384d-a055ac1e34605f4c, us-code-16-2106a-37788d42d32e6540, us-code-33-426e-2-b919ed11d816bce4, us-code-42-12205.-338224f3fe27ab0f`
  evidence: `{"family_margin": -0.999868236549, "hint_id": "modal-synthesis-27f8d4663cad60bd", "predicted_family": "conditional_normative", "priority": 0.999996949267, "sample_id": "us-code-21-384d-a055ac1e34605f4c", "target_family": "frame", "target_probability": 3.050733e-06}`
  evidence: `{"family_margin": -0.987892605306, "hint_id": "modal-synthesis-8a5313d30afadebb", "predicted_family": "frame", "priority": 0.995044103468, "sample_id": "us-code-33-426e-2-b919ed11d816bce4", "target_family": "deontic", "target_probability": 0.004955896532}`
  evidence: `{"family_margin": -0.633195772991, "hint_id": "modal-synthesis-c34ed3f964767899", "predicted_family": "frame", "priority": 0.929442511763, "sample_id": "us-code-42-12205.-338224f3fe27ab0f", "target_family": "conditional_normative", "target_probability": 0.070557488237}`
  evidence: `{"family_margin": -0.890644758809, "hint_id": "modal-synthesis-ca27a065903dc79a", "predicted_family": "frame", "priority": 0.996375317903, "sample_id": "us-code-16-2106a-37788d42d32e6540", "target_family": "deontic", "target_probability": 0.003624682097}`
- `program-806aaf4ed07b78c1`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-094bfa682f6eb802` score `0.982117`
  loss: `autoencoder_residual_cluster` = `0.930918506624`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-9858f.-0a6c449d9ea88b4f, us-code-33-2333-bc5b9a90708f4982, us-code-49-6504.-4df1913a41aa0700, us-code-5-8193-0e69b3c69287e350`
  evidence: `{"family_margin": -0.744064771487, "hint_id": "modal-synthesis-1310c6324541a591", "predicted_family": "deontic", "priority": 0.973943867327, "sample_id": "us-code-49-6504.-4df1913a41aa0700", "target_family": "temporal", "target_probability": 0.026056132673}`
  evidence: `{"family_margin": -0.977034075112, "hint_id": "modal-synthesis-5065991f56674808", "predicted_family": "frame", "priority": 0.989115279983, "sample_id": "us-code-33-2333-bc5b9a90708f4982", "target_family": "deontic", "target_probability": 0.010884720017}`
  evidence: `{"family_margin": -0.149379843055, "hint_id": "modal-synthesis-56dcb04a6b8d2593", "predicted_family": "deontic", "priority": 0.760618202245, "sample_id": "us-code-5-8193-0e69b3c69287e350", "target_family": "temporal", "target_probability": 0.239381797755}`
  evidence: `{"family_margin": -0.952547128602, "hint_id": "modal-synthesis-e254980212ac8261", "predicted_family": "conditional_normative", "priority": 0.999996676942, "sample_id": "us-code-42-9858f.-0a6c449d9ea88b4f", "target_family": "deontic", "target_probability": 3.323058e-06}`
