# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-30787d576e0694b2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-30787d576e0694b2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.919723991007`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-4370d.-bb603ed61730713f, us-code-36-30304-0b23c1753243b86c, us-code-5-418-de842a2d8c1aedd4, us-code-22-9532-7da7d6963d8c4f1a`
  evidence: `{"family_margin": -0.940823512233, "hint_id": "modal-synthesis-67cc8564c277a5ef", "predicted_family": "frame", "priority": 1.090823512233, "sample_id": "us-code-36-30304-0b23c1753243b86c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.633195772991, "hint_id": "modal-synthesis-807fbe84755b5ce0", "predicted_family": "frame", "priority": 0.783195772991, "sample_id": "us-code-5-418-de842a2d8c1aedd4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.993652129001, "hint_id": "modal-synthesis-bff66c441558659e", "predicted_family": "frame", "priority": 1.143652129001, "sample_id": "us-code-42-4370d.-bb603ed61730713f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.511224549803, "hint_id": "modal-synthesis-c9936e4a8ca3cd10", "predicted_family": "temporal", "priority": 0.661224549803, "sample_id": "us-code-22-9532-7da7d6963d8c4f1a", "target_family": "conditional_normative"}`
- `program-423edcd771506a6f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-30787d576e0694b2` score `0.987245`
  loss: `autoencoder_residual_cluster` = `0.795997825496`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-36-151711-f16ce2b197078b60, us-code-38-7105A-fcf06bab2445fce1, us-code-16-366-83baa05ec62b679e, us-code-46-4305.-9d1d567673716470`
  evidence: `{"family_margin": -0.507478180282, "hint_id": "modal-synthesis-16cf700d12baa201", "predicted_family": "alethic", "priority": 0.657478180282, "sample_id": "us-code-16-366-83baa05ec62b679e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.463831688409, "hint_id": "modal-synthesis-24a27bd3e25b0cc6", "predicted_family": "frame", "priority": 0.613831688409, "sample_id": "us-code-46-4305.-9d1d567673716470", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.907898318806, "hint_id": "modal-synthesis-bfc8e63d57cb17a1", "predicted_family": "frame", "priority": 1.057898318806, "sample_id": "us-code-36-151711-f16ce2b197078b60", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.704783114489, "hint_id": "modal-synthesis-c0e46d9496dd7f6a", "predicted_family": "frame", "priority": 0.854783114489, "sample_id": "us-code-38-7105A-fcf06bab2445fce1", "target_family": "deontic"}`
