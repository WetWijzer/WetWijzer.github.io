# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-e44de58a558879f2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->alethic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e44de58a558879f2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.570093354936`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-1445-2910255cee5ce658, us-code-22-8903-987f2f8d788186ac`
  evidence: `{"family_margin": -0.487420205792, "hint_id": "modal-synthesis-0cf354e8cd88cff2", "predicted_family": "frame", "priority": 0.637420205792, "sample_id": "us-code-10-1445-2910255cee5ce658", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.352766504081, "hint_id": "modal-synthesis-7bf08eed6031095b", "predicted_family": "deontic", "priority": 0.502766504081, "sample_id": "us-code-22-8903-987f2f8d788186ac", "target_family": "conditional_normative"}`
- `program-0678cfe6bd005187`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","conditional_normative->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e44de58a558879f2` score `0.990314`
  loss: `autoencoder_residual_cluster` = `0.459117889265`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-540B-9e40f12bc0782de7, us-code-15-2665-22ba978689e710b3`
  evidence: `{"family_margin": -0.350189388673, "hint_id": "modal-synthesis-b980771c9fc89ae3", "predicted_family": "conditional_normative", "priority": 0.500189388673, "sample_id": "us-code-28-540B-9e40f12bc0782de7", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.268046389856, "hint_id": "modal-synthesis-c9e1685bf47f0fa5", "predicted_family": "alethic", "priority": 0.418046389856, "sample_id": "us-code-15-2665-22ba978689e710b3", "target_family": "deontic"}`
