# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-5889b17f54942e78`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5889b17f54942e78` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.126771354801`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-4102-c9ded8769ebbd704, us-code-10-844-e75545e37b61e57f`
  evidence: `{"family_margin": -0.964360748839, "hint_id": "modal-synthesis-8f2addec4751fd8c", "predicted_family": "frame", "priority": 1.114360748839, "sample_id": "us-code-10-844-e75545e37b61e57f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.989181960764, "hint_id": "modal-synthesis-9907d242d784f647", "predicted_family": "temporal", "priority": 1.139181960764, "sample_id": "us-code-38-4102-c9ded8769ebbd704", "target_family": "deontic"}`
- `program-e9d36c062da677a6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5889b17f54942e78` score `0.987664`
  loss: `autoencoder_residual_cluster` = `0.642567035491`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-14103.-3ceb982d686d8535, us-code-29-3205-ced7e5263c5303f7`
  evidence: `{"family_margin": -0.985134070983, "hint_id": "modal-synthesis-18632b296cc062f5", "predicted_family": "frame", "priority": 1.135134070983, "sample_id": "us-code-49-14103.-3ceb982d686d8535", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ff56298caab3a276", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-29-3205-ced7e5263c5303f7", "target_family": "deontic"}`
- `program-1889c92d9e20b08c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5889b17f54942e78` score `0.977389`
  loss: `autoencoder_residual_cluster` = `1.110165115093`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-346a-2-1851abc58a52fa21, us-code-49-20116.-87ead7ff9bdf923b`
  evidence: `{"family_margin": -0.926557636031, "hint_id": "modal-synthesis-2a3a415fb0d191ec", "predicted_family": "conditional_normative", "priority": 1.076557636031, "sample_id": "us-code-49-20116.-87ead7ff9bdf923b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.993772594155, "hint_id": "modal-synthesis-45fa0470d43440d6", "predicted_family": "frame", "priority": 1.143772594155, "sample_id": "us-code-16-346a-2-1851abc58a52fa21", "target_family": "temporal"}`
- `program-1889a3fd503dc053`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5889b17f54942e78` score `0.972584`
  loss: `autoencoder_residual_cluster` = `0.528590816819`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-11501.-5bacf24163dce496, us-code-26-5604-65bee4795c1bed4f, us-code-42-9859.-efaf6c91f0efad0f`
  evidence: `{"family_margin": -0.999964599906, "hint_id": "modal-synthesis-282586de5b494938", "predicted_family": "frame", "priority": 1.149964599906, "sample_id": "us-code-49-11501.-5bacf24163dce496", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.148758388224, "hint_id": "modal-synthesis-c880e6130586c0e3", "predicted_family": "frame", "priority": 0.298758388224, "sample_id": "us-code-26-5604-65bee4795c1bed4f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.012950537672, "hint_id": "modal-synthesis-dd60bd025b276b81", "predicted_family": "frame", "priority": 0.137049462328, "sample_id": "us-code-42-9859.-efaf6c91f0efad0f", "target_family": "frame"}`
