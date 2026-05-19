# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-44e9411d701d3e37`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->temporal","epistemic->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-44e9411d701d3e37` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.347378741649`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-1944-a2b9c9eaeacf5bf7, us-code-22-2734f-015697e8ac5bf2ec, us-code-16-2901-9eff43d26a124a28`
  evidence: `{"family_margin": -0.190822095789, "hint_id": "modal-synthesis-1f1d7c5176d17b54", "predicted_family": "deontic", "priority": 0.340822095789, "sample_id": "us-code-22-2734f-015697e8ac5bf2ec", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ac1019859b362445", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-16-2901-9eff43d26a124a28", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.401314129159, "hint_id": "modal-synthesis-d10c3f633e247133", "predicted_family": "alethic", "priority": 0.551314129159, "sample_id": "us-code-7-1944-a2b9c9eaeacf5bf7", "target_family": "deontic"}`
