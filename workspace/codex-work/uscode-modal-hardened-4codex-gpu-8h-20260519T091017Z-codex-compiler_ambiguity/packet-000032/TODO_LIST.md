# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-f65ac49d55175ec9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f65ac49d55175ec9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.553141087865`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-637-0720c1c2250fc9b4, us-code-22-1642c-08c79f76662ee13b, us-code-50-2425.-47b48c36c06bff21`
  evidence: `{"family_margin": -0.241161539133, "hint_id": "modal-synthesis-3489b7252ca6a15a", "predicted_family": "temporal", "priority": 0.391161539133, "sample_id": "us-code-22-1642c-08c79f76662ee13b", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.031704643574, "hint_id": "modal-synthesis-4bef07d88171660e", "predicted_family": "deontic", "priority": 0.118295356426, "sample_id": "us-code-50-2425.-47b48c36c06bff21", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999966368036, "hint_id": "modal-synthesis-d0c7bf1b10a972af", "predicted_family": "frame", "priority": 1.149966368036, "sample_id": "us-code-15-637-0720c1c2250fc9b4", "target_family": "deontic"}`
