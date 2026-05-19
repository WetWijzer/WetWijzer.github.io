# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-6c8fbb8adc5c4624`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6c8fbb8adc5c4624` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.754559309022`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-30-22-41b0706c6dfe0563, us-code-10-2452-9f8cf05c0b023e33, us-code-2-1612-e16ee1803f4650eb`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-32abc49efbb619fb", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-2-1612-e16ee1803f4650eb", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.968177985389, "hint_id": "modal-synthesis-867875cd9eb166db", "predicted_family": "frame", "priority": 1.118177985389, "sample_id": "us-code-30-22-41b0706c6dfe0563", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.845499941677, "hint_id": "modal-synthesis-edf00fc3490f7378", "predicted_family": "frame", "priority": 0.995499941677, "sample_id": "us-code-10-2452-9f8cf05c0b023e33", "target_family": "deontic"}`
