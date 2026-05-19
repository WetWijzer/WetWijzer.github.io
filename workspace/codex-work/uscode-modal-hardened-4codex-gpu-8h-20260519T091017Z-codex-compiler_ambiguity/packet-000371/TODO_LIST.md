# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-593180d41885004e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-593180d41885004e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.910748794977`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-44-726.-9ba99f9695a05c64, us-code-10-8761a-f20006898ff8c3e4, us-code-15-4652-c7d562053cccf08d`
  evidence: `{"family_margin": -0.72561328302, "hint_id": "modal-synthesis-3e0cd4ccc5992e2a", "predicted_family": "frame", "priority": 0.87561328302, "sample_id": "us-code-10-8761a-f20006898ff8c3e4", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.667479661137, "hint_id": "modal-synthesis-87507245f24fb37c", "predicted_family": "alethic", "priority": 0.817479661137, "sample_id": "us-code-15-4652-c7d562053cccf08d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.889153440775, "hint_id": "modal-synthesis-e5ece47722242bba", "predicted_family": "frame", "priority": 1.039153440775, "sample_id": "us-code-44-726.-9ba99f9695a05c64", "target_family": "deontic"}`
