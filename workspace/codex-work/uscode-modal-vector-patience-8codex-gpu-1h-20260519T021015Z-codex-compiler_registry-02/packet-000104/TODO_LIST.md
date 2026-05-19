# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-7d31f2f33536b56a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.928031428972`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-460l-32-8496645571674501, us-code-22-262g-3-4598f33f9ff83e75, us-code-50-3606.-48486f4a53e6b72a, us-code-20-1128b-9af9d460afd7ab0f`
  evidence: `{"family_margin": -0.999681881453, "hint_id": "modal-synthesis-2275ddd60b97169c", "predicted_family": "frame", "priority": 0.999908596496, "sample_id": "us-code-16-460l-32-8496645571674501", "target_family": "conditional_normative", "target_probability": 9.1403504e-05}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-6cc0fa128c6ec69c", "predicted_family": "frame", "priority": 0.918866010745, "sample_id": "us-code-50-3606.-48486f4a53e6b72a", "target_family": "deontic", "target_probability": 0.081133989255}`
  evidence: `{"family_margin": -0.816824589024, "hint_id": "modal-synthesis-d802a5a437785724", "predicted_family": "frame", "priority": 0.919118075131, "sample_id": "us-code-22-262g-3-4598f33f9ff83e75", "target_family": "deontic", "target_probability": 0.080881924869}`
  evidence: `{"family_margin": -0.716265383189, "hint_id": "modal-synthesis-e8ab22f5ee64dc41", "predicted_family": "alethic", "priority": 0.874233033517, "sample_id": "us-code-20-1128b-9af9d460afd7ab0f", "target_family": "deontic", "target_probability": 0.125766966483}`
- `program-47e90120b9995fdd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `0.972648`
  loss: `autoencoder_residual_cluster` = `0.775273579079`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-50-3093.-00f06b1f3a2a4241, us-code-16-538a-5ea2c3a516d316aa, us-code-42-285d-db02943ba9789a11`
  evidence: `{"family_margin": -0.997438838502, "hint_id": "modal-synthesis-01ad7d672fcf2716", "predicted_family": "conditional_normative", "priority": 0.999989320726, "sample_id": "us-code-50-3093.-00f06b1f3a2a4241", "target_family": "deontic", "target_probability": 1.0679274e-05}`
  evidence: `{"family_margin": -0.53334883072, "hint_id": "modal-synthesis-af9b558e39ffd078", "predicted_family": "conditional_normative", "priority": 0.772810010596, "sample_id": "us-code-16-538a-5ea2c3a516d316aa", "target_family": "deontic", "target_probability": 0.227189989404}`
  evidence: `{"family_margin": 0.145299598073, "hint_id": "modal-synthesis-bceab1302fac0410", "predicted_family": "deontic", "priority": 0.553021405916, "sample_id": "us-code-42-285d-db02943ba9789a11", "target_family": "deontic", "target_probability": 0.446978594084}`
- `program-323e244dbaadd2ce`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","conditional_normative->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `0.955221`
  loss: `autoencoder_residual_cluster` = `0.930935928215`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-43-1747.-b8d5f357b1d91a8e, us-code-26-7476-14666158c64390c3, us-code-16-459j-8-ed4fbf0da24947d1`
  evidence: `{"family_margin": -0.905148252615, "hint_id": "modal-synthesis-8443446d82f96bc4", "predicted_family": "conditional_normative", "priority": 0.952574126876, "sample_id": "us-code-26-7476-14666158c64390c3", "target_family": "temporal", "target_probability": 0.047425873124}`
  evidence: `{"family_margin": -0.995576220956, "hint_id": "modal-synthesis-c1dc29866843e610", "predicted_family": "conditional_normative", "priority": 0.999683971207, "sample_id": "us-code-43-1747.-b8d5f357b1d91a8e", "target_family": "deontic", "target_probability": 0.000316028793}`
  evidence: `{"family_margin": -0.641210976056, "hint_id": "modal-synthesis-ea0712dd814b247c", "predicted_family": "temporal", "priority": 0.840549686562, "sample_id": "us-code-16-459j-8-ed4fbf0da24947d1", "target_family": "deontic", "target_probability": 0.159450313438}`
