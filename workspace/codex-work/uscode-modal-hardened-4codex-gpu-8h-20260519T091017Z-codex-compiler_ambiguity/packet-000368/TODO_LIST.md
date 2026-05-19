# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4b9753511c3f966f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4b9753511c3f966f` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.857745939774`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-10302-92aef49cf32dc7b8, us-code-20-1087e-eff08efbdaff3a56, us-code-36-170506-d2b99e2b9b52b63c`
  evidence: `{"family_margin": -0.887894843716, "hint_id": "modal-synthesis-311cca866c012838", "predicted_family": "frame", "priority": 1.037894843716, "sample_id": "us-code-10-10302-92aef49cf32dc7b8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-8b376431ee26cde6", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-36-170506-d2b99e2b9b52b63c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.655142606276, "hint_id": "modal-synthesis-8d4db91f4d16c456", "predicted_family": "alethic", "priority": 0.805142606276, "sample_id": "us-code-20-1087e-eff08efbdaff3a56", "target_family": "conditional_normative"}`
