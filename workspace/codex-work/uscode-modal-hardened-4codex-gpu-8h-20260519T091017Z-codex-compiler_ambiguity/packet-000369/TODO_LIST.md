# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-286339d1f28e6083`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.929293683301`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-45L-42236fa7dda0591e, us-code-16-410n-d27716bf4667f350`
  evidence: `{"family_margin": -0.819948970608, "hint_id": "modal-synthesis-3e459236fb1bd2f4", "predicted_family": "frame", "priority": 0.969948970608, "sample_id": "us-code-26-45L-42236fa7dda0591e", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.738638395995, "hint_id": "modal-synthesis-b9fc8f9a1ff5b6c9", "predicted_family": "deontic", "priority": 0.888638395995, "sample_id": "us-code-16-410n-d27716bf4667f350", "target_family": "conditional_normative"}`
- `program-425c9be56603b9ac`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.977172`
  loss: `autoencoder_residual_cluster` = `0.505941793204`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-1276-78104eb1d3b59bd3, us-code-22-7402-f13b16a29fa68295, us-code-20-1078-10-192bae91a06078eb`
  evidence: `{"family_margin": -0.830738257014, "hint_id": "modal-synthesis-df24e043c959628f", "predicted_family": "deontic", "priority": 0.980738257014, "sample_id": "us-code-33-1276-78104eb1d3b59bd3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.224697529935, "hint_id": "modal-synthesis-e6fd5dfc78612f72", "predicted_family": "frame", "priority": 0.374697529935, "sample_id": "us-code-22-7402-f13b16a29fa68295", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.012389592663, "hint_id": "modal-synthesis-f4894eefcc3a5d48", "predicted_family": "conditional_normative", "priority": 0.162389592663, "sample_id": "us-code-20-1078-10-192bae91a06078eb", "target_family": "deontic"}`
- `program-c15bcba3a19952a5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.971003`
  loss: `autoencoder_residual_cluster` = `0.573589270628`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-46-30105.-024fee1fbe6f67ee, us-code-22-866-be9f23427595bfe1`
  evidence: `{"family_margin": 0.144667398472, "hint_id": "modal-synthesis-8371bbfd53d636b0", "predicted_family": "temporal", "priority": 0.005332601528, "sample_id": "us-code-22-866-be9f23427595bfe1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.991845939729, "hint_id": "modal-synthesis-d9cd093617e0be30", "predicted_family": "frame", "priority": 1.141845939729, "sample_id": "us-code-46-30105.-024fee1fbe6f67ee", "target_family": "temporal"}`
- `program-cfcbff554f78be50`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.943209`
  loss: `autoencoder_residual_cluster` = `0.760338497159`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1320a-19cde0462c72cc39, us-code-26-6050J-5b6ef7c634b15989, us-code-15-7407-a39ea8637eeb8bc6, us-code-50-3040.-9d91aee75289e33b`
  evidence: `{"family_margin": -0.125156415541, "hint_id": "modal-synthesis-0f152963ce5f41b6", "predicted_family": "temporal", "priority": 0.275156415541, "sample_id": "us-code-50-3040.-9d91aee75289e33b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.53369122802, "hint_id": "modal-synthesis-88c057196c11c3b7", "predicted_family": "temporal", "priority": 0.68369122802, "sample_id": "us-code-15-7407-a39ea8637eeb8bc6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.941814049738, "hint_id": "modal-synthesis-af2abd8ba60b5e76", "predicted_family": "frame", "priority": 1.091814049738, "sample_id": "us-code-42-1320a-19cde0462c72cc39", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.840692295338, "hint_id": "modal-synthesis-bfdcb032c76f254c", "predicted_family": "frame", "priority": 0.990692295338, "sample_id": "us-code-26-6050J-5b6ef7c634b15989", "target_family": "temporal"}`
