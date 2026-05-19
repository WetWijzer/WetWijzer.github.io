# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-launch-diagnostic3-20260519T071948Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-launch-diagnostic3-20260519T071948Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-eb828901adafd41c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-eb828901adafd41c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.393593746423`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-3171-25fb9415d0215f89, us-code-28-639-3f6a9bd848b43a0f, us-code-42-12623.-3bb0ba584243da4d, us-code-28-657-46ef5fa4f2d7343c`
  evidence: `{"family_margin": -0.024420676493, "hint_id": "modal-synthesis-410272094173acde", "predicted_family": "deontic", "priority": 0.174420676493, "sample_id": "us-code-28-657-46ef5fa4f2d7343c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.225664315371, "hint_id": "modal-synthesis-7a213442ec039763", "predicted_family": "frame", "priority": 0.375664315371, "sample_id": "us-code-28-639-3f6a9bd848b43a0f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.121737687132, "hint_id": "modal-synthesis-9325631464b52155", "predicted_family": "frame", "priority": 0.271737687132, "sample_id": "us-code-42-12623.-3bb0ba584243da4d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.602552306694, "hint_id": "modal-synthesis-a0f159648fb0de75", "predicted_family": "temporal", "priority": 0.752552306694, "sample_id": "us-code-7-3171-25fb9415d0215f89", "target_family": "epistemic"}`
