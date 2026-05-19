# packet-000226

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000226/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000226/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000226-20260519_030004

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-56423682081208fb` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-56423682081208fb` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999847673458, "hint_id": "modal-synthesis-8552f6ab611e6096", "predicted_family": "frame", "priority": 1.149847673458, "sample_id": "us-code-10-7802-e1bc3255fecd6e31", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999987711651, "hint_id": "modal-synthesis-e311ff880589de31", "predicted_family": "temporal", "priority": 1.149987711651, "sample_id": "us-code-5-2105-dc9193f5ddf8bbab", "target_family": "conditional_normative"}`
- `program-38bf74aebd90ed2a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-56423682081208fb` score `0.985476`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.390318016707, "hint_id": "modal-synthesis-47bf43c4d05de643", "predicted_family": "deontic", "priority": 0.540318016707, "sample_id": "us-code-25-161b-04160365a0fa3962", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.957002846935, "hint_id": "modal-synthesis-b64b09fc47735816", "predicted_family": "frame", "priority": 1.107002846935, "sample_id": "us-code-7-1727a-69bf4e9f23589220", "target_family": "deontic"}`
- `program-bb30cb81212858f8` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->dynamic","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-56423682081208fb` score `0.966469`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.435322306111, "hint_id": "modal-synthesis-121c62798ac72db0", "predicted_family": "deontic", "priority": 0.585322306111, "sample_id": "us-code-34-40916-38292e1c50f1b0a2", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.39812025136, "hint_id": "modal-synthesis-6a66863885734d15", "predicted_family": "deontic", "priority": 0.54812025136, "sample_id": "us-code-10-20217-43a61c94da6a8a5f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.929753832998, "hint_id": "modal-synthesis-80caabd3f79a776f", "predicted_family": "conditional_normative", "priority": 1.079753832998, "sample_id": "us-code-5-6336-01b727a3a3d92fa6", "target_family": "dynamic"}`
- `program-aab6433d970c0b79` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-56423682081208fb` score `0.935881`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.977034075112, "hint_id": "modal-synthesis-141988e2526fd51e", "predicted_family": "frame", "priority": 1.127034075112, "sample_id": "us-code-33-2333-bc5b9a90708f4982", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.744064771487, "hint_id": "modal-synthesis-625dd023b6151b45", "predicted_family": "deontic", "priority": 0.894064771487, "sample_id": "us-code-49-6504.-4df1913a41aa0700", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.952547128602, "hint_id": "modal-synthesis-6ad6d47530e9860f", "predicted_family": "conditional_normative", "priority": 1.102547128602, "sample_id": "us-code-42-9858f.-0a6c449d9ea88b4f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.149379843055, "hint_id": "modal-synthesis-dacd1cbdc04545a6", "predicted_family": "deontic", "priority": 0.299379843055, "sample_id": "us-code-5-8193-0e69b3c69287e350", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
