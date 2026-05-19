# packet-000057

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000057/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000057/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000057-20260519_080717

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-75eba3e96cb1fc35` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-75eba3e96cb1fc35` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.042151771569, "hint_id": "modal-synthesis-0f662d71fbb4a60e", "predicted_family": "frame", "priority": 0.192151771569, "sample_id": "us-code-43-4-71ea028bee67bb72", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.987659830267, "hint_id": "modal-synthesis-1cd6a0ca39ae09d6", "predicted_family": "temporal", "priority": 1.137659830267, "sample_id": "us-code-15-4656-8948f7d6d7ef22ee", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.998448998074, "hint_id": "modal-synthesis-295d5e2944cf2656", "predicted_family": "frame", "priority": 1.148448998074, "sample_id": "us-code-2-607-2e9d6e27189ecc14", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.797111365677, "hint_id": "modal-synthesis-b38e3df3862e04b6", "predicted_family": "deontic", "priority": 0.947111365677, "sample_id": "us-code-22-290n-3-2b067e975d5b088d", "target_family": "temporal"}`
- `program-c3adb937685abb4b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-75eba3e96cb1fc35` score `0.993709`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.996442309715, "hint_id": "modal-synthesis-0a8785b3dfb6aa69", "predicted_family": "temporal", "priority": 1.146442309715, "sample_id": "us-code-12-1701q-1-7363f6565593d464", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.116498490285, "hint_id": "modal-synthesis-91c632d4ef7fd250", "predicted_family": "deontic", "priority": 0.033501509715, "sample_id": "us-code-28-755-d77e49748d22301e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.199221055742, "hint_id": "modal-synthesis-cf4cbf6f1eeb1a6e", "predicted_family": "frame", "priority": 0.349221055742, "sample_id": "us-code-15-713a-1-8b5e17a928c198e1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-ddb4f9bdb7aa21b5", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-6-533-f1d9319c09926fa6", "target_family": "temporal"}`
- `program-6b95594450839038` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-75eba3e96cb1fc35` score `0.929642`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.804723328443, "hint_id": "modal-synthesis-4b2b2e9be3d746c6", "predicted_family": "deontic", "priority": 0.954723328443, "sample_id": "us-code-25-344-eef9c2928ad7515a", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.518764260388, "hint_id": "modal-synthesis-ac4b8c8763b6f940", "predicted_family": "deontic", "priority": 0.668764260388, "sample_id": "us-code-33-1516-3803c560f593fc1e", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
