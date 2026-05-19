# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-944860b0f9267f91`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-944860b0f9267f91` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.819554333561`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-1354-6747db394be7d16a, us-code-42-5844.-0a161e6c2d8d9e38, us-code-2-194b-c95de1cc8c49a0e9, us-code-20-1059b-743ed93e96671aec`
  evidence: `{"family_margin": -0.970679750509, "hint_id": "modal-synthesis-09f6c8bea39288b6", "predicted_family": "frame", "priority": 1.120679750509, "sample_id": "us-code-22-1354-6747db394be7d16a", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.785893947088, "hint_id": "modal-synthesis-3e1251dd56db2e91", "predicted_family": "frame", "priority": 0.935893947088, "sample_id": "us-code-2-194b-c95de1cc8c49a0e9", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-6c215ff20c268f58", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-20-1059b-743ed93e96671aec", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.921643636648, "hint_id": "modal-synthesis-f7e3479bc63339dc", "predicted_family": "frame", "priority": 1.071643636648, "sample_id": "us-code-42-5844.-0a161e6c2d8d9e38", "target_family": "deontic"}`
- `program-dbc7ffb50949a0b6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-944860b0f9267f91` score `0.978296`
  loss: `autoencoder_residual_cluster` = `0.760167221798`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-14705.-ce33e074ffa4430f, us-code-8-1186-866b0788007b45ad, us-code-43-737.-159ba480db3e5864, us-code-13-184-f64c50d8f2db025c`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1a0b9fa04c895e3e", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-13-184-f64c50d8f2db025c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.628952442126, "hint_id": "modal-synthesis-46427d6fe7af9293", "predicted_family": "frame", "priority": 0.778952442126, "sample_id": "us-code-43-737.-159ba480db3e5864", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-6111eba8e3b5475b", "predicted_family": "frame", "priority": 0.982441698483, "sample_id": "us-code-8-1186-866b0788007b45ad", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.979274746583, "hint_id": "modal-synthesis-d2a527567d9cf5ac", "predicted_family": "frame", "priority": 1.129274746583, "sample_id": "us-code-49-14705.-ce33e074ffa4430f", "target_family": "temporal"}`
- `program-3a621d9671d9c4f9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-944860b0f9267f91` score `0.967991`
  loss: `autoencoder_residual_cluster` = `0.477468094767`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-2209j-dd7e2e5d9e16255f, us-code-35-181-f29b71497947aab0, us-code-12-2153-baf813aee2fd8501`
  evidence: `{"family_margin": -0.982627491034, "hint_id": "modal-synthesis-32452ee106a731a4", "predicted_family": "frame", "priority": 1.132627491034, "sample_id": "us-code-7-2209j-dd7e2e5d9e16255f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.138132227584, "hint_id": "modal-synthesis-5fa38d19a6cb6af5", "predicted_family": "deontic", "priority": 0.011867772416, "sample_id": "us-code-12-2153-baf813aee2fd8501", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.137909020851, "hint_id": "modal-synthesis-7429647ed7f83371", "predicted_family": "deontic", "priority": 0.287909020851, "sample_id": "us-code-35-181-f29b71497947aab0", "target_family": "temporal"}`
