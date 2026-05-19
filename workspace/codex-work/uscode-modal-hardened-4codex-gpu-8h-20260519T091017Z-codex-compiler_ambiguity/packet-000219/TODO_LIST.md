# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-59df8f42a91c0f60`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59df8f42a91c0f60` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.878624297195`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-50-98h-81e88eb05f5b95c6, us-code-16-460nnn-72-a7c1871912514db1, us-code-12-2279a-3-e50f61df5c1d28a1`
  evidence: `{"family_margin": -0.9045986346, "hint_id": "modal-synthesis-0f3cad1855dde519", "predicted_family": "frame", "priority": 1.0545986346, "sample_id": "us-code-50-98h-81e88eb05f5b95c6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.663964931589, "hint_id": "modal-synthesis-e64f753aa22b56e9", "predicted_family": "deontic", "priority": 0.813964931589, "sample_id": "us-code-16-460nnn-72-a7c1871912514db1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.617309325395, "hint_id": "modal-synthesis-f6e12b83d1c4b943", "predicted_family": "frame", "priority": 0.767309325395, "sample_id": "us-code-12-2279a-3-e50f61df5c1d28a1", "target_family": "temporal"}`
