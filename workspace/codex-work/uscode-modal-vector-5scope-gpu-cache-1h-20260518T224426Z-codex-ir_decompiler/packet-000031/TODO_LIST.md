# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-9bd7469d29661bf0`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-9bd7469d29661bf0` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.334827929473`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-25-2453-6148409606ae76c3, us-code-21-360ccc-2-1dfff84fbecab91a, us-code-48-912.-591af0277276625b, us-code-18-9-b33f6d6a250bd8aa`
  evidence: `{"cosine_similarity": 0.044685397113, "hint_id": "modal-synthesis-4c7e057acaaa33a0", "priority": 0.399878073115, "reconstruction_loss": 0.399878073115, "sample_id": "us-code-25-2453-6148409606ae76c3"}`
  evidence: `{"cosine_similarity": 0.434773424891, "hint_id": "modal-synthesis-7bf7685eb1a9171c", "priority": 0.281865141048, "reconstruction_loss": 0.281865141048, "sample_id": "us-code-48-912.-591af0277276625b"}`
  evidence: `{"cosine_similarity": 0.264333586782, "hint_id": "modal-synthesis-88fd1a92228db5e6", "priority": 0.266796957902, "reconstruction_loss": 0.266796957902, "sample_id": "us-code-18-9-b33f6d6a250bd8aa"}`
  evidence: `{"cosine_similarity": 0.149104087326, "hint_id": "modal-synthesis-dbc98de613b444d0", "priority": 0.390771545825, "reconstruction_loss": 0.390771545825, "sample_id": "us-code-21-360ccc-2-1dfff84fbecab91a"}`
