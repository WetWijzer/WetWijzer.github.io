# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-e9bfe06262fc7e05`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","deontic->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e9bfe06262fc7e05` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.927987216317`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-376-3ca56b96c9476e4b, us-code-10-2350p-e57d9c10eedfdef1`
  evidence: `{"family_margin": -0.555974845748, "hint_id": "modal-synthesis-4345a801a83bd168", "predicted_family": "deontic", "priority": 0.705974845748, "sample_id": "us-code-10-2350p-e57d9c10eedfdef1", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999586886, "hint_id": "modal-synthesis-75181e2a55e8cc94", "predicted_family": "alethic", "priority": 1.149999586886, "sample_id": "us-code-28-376-3ca56b96c9476e4b", "target_family": "conditional_normative"}`
