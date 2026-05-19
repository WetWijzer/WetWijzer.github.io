# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-9074e2b6504fa9be`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9074e2b6504fa9be` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.928182226577`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-19-1623-55dbed701beac8c4, us-code-2-6618-c0019bb488a37bdd`
  evidence: `{"family_margin": -0.999999999985, "hint_id": "modal-synthesis-4da9ed5e7d787d84", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-19-1623-55dbed701beac8c4", "target_family": "temporal", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.500094313565, "hint_id": "modal-synthesis-77a05d7130e94990", "predicted_family": "frame", "priority": 0.856364453154, "sample_id": "us-code-2-6618-c0019bb488a37bdd", "target_family": "conditional_normative", "target_probability": 0.143635546846}`
- `program-f6c0de4ebcf9a4e9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->epistemic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9074e2b6504fa9be` score `0.970185`
  loss: `autoencoder_residual_cluster` = `0.802804095431`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-4851.-e3beec5f0d5875eb, us-code-19-66-c0f75ec4564c0501`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-aa431f0f916f66d3", "predicted_family": "temporal", "priority": 0.622281006034, "sample_id": "us-code-19-66-c0f75ec4564c0501", "target_family": "temporal", "target_probability": 0.377718993966}`
  evidence: `{"family_margin": -0.893632049076, "hint_id": "modal-synthesis-ee4fc5e1d3c89188", "predicted_family": "alethic", "priority": 0.983327184828, "sample_id": "us-code-42-4851.-e3beec5f0d5875eb", "target_family": "epistemic", "target_probability": 0.016672815172}`
- `program-3b27ec3c17703f88`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9074e2b6504fa9be` score `0.954788`
  loss: `autoencoder_residual_cluster` = `0.871539295783`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-5841.-ff27bf181f6227ac, us-code-42-1862n-d77569aa22b1ae2f, us-code-10-3070-f929a4596538ab5a`
  evidence: `{"family_margin": -0.989970952516, "hint_id": "modal-synthesis-3f6ecd86e697a016", "predicted_family": "frame", "priority": 0.995033677159, "sample_id": "us-code-42-1862n-d77569aa22b1ae2f", "target_family": "deontic", "target_probability": 0.004966322841}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-ae53817f9137ec94", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-42-5841.-ff27bf181f6227ac", "target_family": "dynamic", "target_probability": 0.0}`
  evidence: `{"family_margin": 0.149681949852, "hint_id": "modal-synthesis-af0bd3f12836055c", "predicted_family": "deontic", "priority": 0.619584210189, "sample_id": "us-code-10-3070-f929a4596538ab5a", "target_family": "deontic", "target_probability": 0.380415789811}`
