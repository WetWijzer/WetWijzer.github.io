# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4ccc55b8f1b83151`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-4ccc55b8f1b83151` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.455721508241`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-38-1722A-36a73cb7e6dbf73e, us-code-29-794c-686bfc4da3dd44d6, us-code-42-5041-53ccc938f3473016, us-code-36-21705-3316728336d2c123`
  evidence: `{"cosine_similarity": -0.066331679647, "hint_id": "modal-synthesis-312b602e5fb1680d", "priority": 0.419096848998, "reconstruction_loss": 0.419096848998, "sample_id": "us-code-36-21705-3316728336d2c123"}`
  evidence: `{"cosine_similarity": -0.224225263833, "hint_id": "modal-synthesis-896fa4e9fcef694b", "priority": 0.47797374648, "reconstruction_loss": 0.47797374648, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e"}`
  evidence: `{"cosine_similarity": -0.448760861403, "hint_id": "modal-synthesis-daa02ea10baba0cd", "priority": 0.461261702004, "reconstruction_loss": 0.461261702004, "sample_id": "us-code-42-5041-53ccc938f3473016"}`
  evidence: `{"cosine_similarity": -0.038886576724, "hint_id": "modal-synthesis-f4c1b511688795e5", "priority": 0.464553735483, "reconstruction_loss": 0.464553735483, "sample_id": "us-code-29-794c-686bfc4da3dd44d6"}`
