# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-ef6b99cd4e339e3e`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-ef6b99cd4e339e3e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.559357265965`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-36-904-23d13763f249af22, us-code-42-18363.-2c1c33e4b656cb38, us-code-12-2279aa-2-6a09ee84391e5f19, us-code-42-8262g.-4d0259caef5347ae`
  evidence: `{"cosine_similarity": 0.324418763621, "hint_id": "modal-synthesis-1d53ea970a1a1816", "priority": 0.275042659172, "reconstruction_loss": 0.275042659172, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19"}`
  evidence: `{"cosine_similarity": -0.759276386399, "hint_id": "modal-synthesis-60a89ffeb94b56a8", "priority": 0.957229707661, "reconstruction_loss": 0.957229707661, "sample_id": "us-code-36-904-23d13763f249af22"}`
  evidence: `{"cosine_similarity": 0.399483647303, "hint_id": "modal-synthesis-6d25193602eeba8e", "priority": 0.265579222737, "reconstruction_loss": 0.265579222737, "sample_id": "us-code-42-8262g.-4d0259caef5347ae"}`
  evidence: `{"cosine_similarity": -0.35377637053, "hint_id": "modal-synthesis-9d58ff6911a0056d", "priority": 0.73957747429, "reconstruction_loss": 0.73957747429, "sample_id": "us-code-42-18363.-2c1c33e4b656cb38"}`
