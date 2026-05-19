# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-5993fda4a993add6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5993fda4a993add6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.827545442558`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-7351d-4e93e049fc664c18, us-code-42-14101.-a5beabd50f2754c9, us-code-33-1107-bb564d15a0040608`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-1bfa8403c3bb2bb0", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-42-14101.-a5beabd50f2754c9", "target_family": "deontic", "target_probability": 0.168731311045}`
  evidence: `{"family_margin": -0.224993730737, "hint_id": "modal-synthesis-74367943cee3c2db", "predicted_family": "frame", "priority": 0.653173495461, "sample_id": "us-code-33-1107-bb564d15a0040608", "target_family": "deontic", "target_probability": 0.346826504539}`
  evidence: `{"family_margin": -0.981612997966, "hint_id": "modal-synthesis-de62869ebd7211b3", "predicted_family": "frame", "priority": 0.998194143259, "sample_id": "us-code-20-7351d-4e93e049fc664c18", "target_family": "conditional_normative", "target_probability": 0.001805856741}`
