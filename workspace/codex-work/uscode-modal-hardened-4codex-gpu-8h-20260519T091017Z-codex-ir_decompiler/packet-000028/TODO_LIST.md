# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-b12c19ba39527b29`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-b12c19ba39527b29` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.374510327609`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-46-12107.-ac993296d58346dd, us-code-16-198a-69c109aec60f214a, us-code-22-1642e-0a4a6e0aa906f829, us-code-25-450a-1-b25ed1d7e3a8d3a7`
  evidence: `{"cosine_similarity": 0.21831952826, "hint_id": "modal-synthesis-0c5221fa19d17cf3", "priority": 0.393930054009, "reconstruction_loss": 0.393930054009, "sample_id": "us-code-16-198a-69c109aec60f214a"}`
  evidence: `{"cosine_similarity": 0.254358231612, "hint_id": "modal-synthesis-1edb15cbeacdff7e", "priority": 0.276060016095, "reconstruction_loss": 0.276060016095, "sample_id": "us-code-25-450a-1-b25ed1d7e3a8d3a7"}`
  evidence: `{"cosine_similarity": 0.132854920842, "hint_id": "modal-synthesis-699ee0050c4a7e95", "priority": 0.309809220678, "reconstruction_loss": 0.309809220678, "sample_id": "us-code-22-1642e-0a4a6e0aa906f829"}`
  evidence: `{"cosine_similarity": -0.153577077166, "hint_id": "modal-synthesis-cf5250bf4ac196ca", "priority": 0.518242019652, "reconstruction_loss": 0.518242019652, "sample_id": "us-code-46-12107.-ac993296d58346dd"}`
