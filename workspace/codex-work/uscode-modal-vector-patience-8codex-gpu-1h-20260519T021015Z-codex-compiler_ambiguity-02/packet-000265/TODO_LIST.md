# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-59c913bcde9c693d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59c913bcde9c693d` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.897118180434`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-2-1902-9bf1dcbf06b93760, us-code-16-403c-4-96cbffd14ccb8ab5, us-code-18-119-3c8e7e7e47fc634f`
  evidence: `{"family_margin": -0.975764796208, "hint_id": "modal-synthesis-d52154f08351bd32", "predicted_family": "frame", "priority": 1.125764796208, "sample_id": "us-code-16-403c-4-96cbffd14ccb8ab5", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.265589752753, "hint_id": "modal-synthesis-db3e227539f69bd0", "predicted_family": "deontic", "priority": 0.415589752753, "sample_id": "us-code-18-119-3c8e7e7e47fc634f", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.99999999234, "hint_id": "modal-synthesis-e4640901ab9aec88", "predicted_family": "temporal", "priority": 1.14999999234, "sample_id": "us-code-2-1902-9bf1dcbf06b93760", "target_family": "deontic"}`
- `program-584127d8685b696e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59c913bcde9c693d` score `0.983627`
  loss: `autoencoder_residual_cluster` = `0.866597231235`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-3016.-a01430f068ac3201, us-code-42-6341.-175bf33765c9042b, us-code-30-665-75575ae82f97b718`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-37d665571769cd76", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-30-665-75575ae82f97b718", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997326341989, "hint_id": "modal-synthesis-aef47417d4901348", "predicted_family": "temporal", "priority": 1.147326341989, "sample_id": "us-code-42-3016.-a01430f068ac3201", "target_family": "frame"}`
  evidence: `{"family_margin": -0.964745859147, "hint_id": "modal-synthesis-da79806a5d8d2b73", "predicted_family": "frame", "priority": 1.114745859147, "sample_id": "us-code-42-6341.-175bf33765c9042b", "target_family": "deontic"}`
