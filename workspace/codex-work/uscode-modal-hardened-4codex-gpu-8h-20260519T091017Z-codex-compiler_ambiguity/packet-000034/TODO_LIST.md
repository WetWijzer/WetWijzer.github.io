# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-4c25f554081d2bf6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4c25f554081d2bf6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.572733274523`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-7432-850de69c4770f055, us-code-12-1747b-bd0d4aaaab2be128, us-code-42-5420.-00697568aff4296c, us-code-18-3047-8849b73c29ba4ad6`
  evidence: `{"family_margin": -0.199023551178, "hint_id": "modal-synthesis-214b146d9b341c09", "predicted_family": "frame", "priority": 0.349023551178, "sample_id": "us-code-18-3047-8849b73c29ba4ad6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.257100608002, "hint_id": "modal-synthesis-3018c87091dc74b5", "predicted_family": "frame", "priority": 0.407100608002, "sample_id": "us-code-12-1747b-bd0d4aaaab2be128", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.239733197541, "hint_id": "modal-synthesis-3c1c919888e28266", "predicted_family": "temporal", "priority": 0.389733197541, "sample_id": "us-code-42-5420.-00697568aff4296c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.995075741369, "hint_id": "modal-synthesis-73dc8951d9b3112b", "predicted_family": "frame", "priority": 1.145075741369, "sample_id": "us-code-22-7432-850de69c4770f055", "target_family": "temporal"}`
- `program-b50059d37a335da4`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4c25f554081d2bf6` score `0.96741`
  loss: `autoencoder_residual_cluster` = `0.568267473797`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1320c-9cb593b2c76aead9, us-code-35-31-0de5c47d579a648d, us-code-37-419-bb9c6c1b486640d1, us-code-7-8105-c1005974f3a24fed`
  evidence: `{"family_margin": -0.907572549173, "hint_id": "modal-synthesis-1c4f6212468b108e", "predicted_family": "frame", "priority": 1.057572549173, "sample_id": "us-code-42-1320c-9cb593b2c76aead9", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.073838799863, "hint_id": "modal-synthesis-8d9bda4aee1fbf1c", "predicted_family": "deontic", "priority": 0.076161200137, "sample_id": "us-code-7-8105-c1005974f3a24fed", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.411364259811, "hint_id": "modal-synthesis-a6886b9da47a3f8f", "predicted_family": "frame", "priority": 0.561364259811, "sample_id": "us-code-37-419-bb9c6c1b486640d1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.427971886065, "hint_id": "modal-synthesis-cc3e54f9f513cecb", "predicted_family": "temporal", "priority": 0.577971886065, "sample_id": "us-code-35-31-0de5c47d579a648d", "target_family": "deontic"}`
