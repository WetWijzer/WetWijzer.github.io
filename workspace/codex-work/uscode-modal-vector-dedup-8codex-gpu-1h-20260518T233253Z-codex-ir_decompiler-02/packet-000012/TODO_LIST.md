# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-23cd022c87da8def`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-23cd022c87da8def` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.460992976655`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-49-47126.-2322d39a63b9ba2d, us-code-12-639-a6faf86b06383bb9, us-code-22-127-239ab62aacc72ba4, us-code-10-10504-6eab7f295cd6facd`
  evidence: `{"cosine_similarity": -0.187196408289, "hint_id": "modal-synthesis-0175c1b3d2154bba", "priority": 0.580793508157, "reconstruction_loss": 0.580793508157, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d"}`
  evidence: `{"cosine_similarity": 0.206967820011, "hint_id": "modal-synthesis-03e56843d15030fc", "priority": 0.341483437006, "reconstruction_loss": 0.341483437006, "sample_id": "us-code-10-10504-6eab7f295cd6facd"}`
  evidence: `{"cosine_similarity": 0.1496639106, "hint_id": "modal-synthesis-0a7cf8c288d5f61d", "priority": 0.38549095266, "reconstruction_loss": 0.38549095266, "sample_id": "us-code-22-127-239ab62aacc72ba4"}`
  evidence: `{"cosine_similarity": -0.116360077636, "hint_id": "modal-synthesis-6aa39c21e6f90b10", "priority": 0.536204008798, "reconstruction_loss": 0.536204008798, "sample_id": "us-code-12-639-a6faf86b06383bb9"}`
