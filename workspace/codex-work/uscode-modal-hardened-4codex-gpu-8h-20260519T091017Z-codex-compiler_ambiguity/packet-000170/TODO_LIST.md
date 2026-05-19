# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-53d94de9aecf887d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-53d94de9aecf887d` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.134789450856`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-40-6501-21da81a17feed968, us-code-12-5537-d5683383f045327e`
  evidence: `{"family_margin": -0.988612205682, "hint_id": "modal-synthesis-35f1fd249f830c4c", "predicted_family": "frame", "priority": 1.138612205682, "sample_id": "us-code-40-6501-21da81a17feed968", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.98096669603, "hint_id": "modal-synthesis-c39fd7b1fd9785fb", "predicted_family": "frame", "priority": 1.13096669603, "sample_id": "us-code-12-5537-d5683383f045327e", "target_family": "epistemic"}`
