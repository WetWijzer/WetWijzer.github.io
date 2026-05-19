# packet-000044

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_registry-01/packet-000044/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_registry-01/packet-000044/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000044-20260519_015210

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-fff7763164907c54` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-fff7763164907c54` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.952569757822, "hint_id": "modal-synthesis-5055e972a952416a", "predicted_family": "conditional_normative", "priority": 0.99999920791, "sample_id": "us-code-10-1141-753a37a225a7b653", "target_family": "deontic", "target_probability": 7.9209e-07}`
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-7cbaf96f6693a6aa", "predicted_family": "frame", "priority": 0.918078633988, "sample_id": "us-code-42-7385.-4f48c347ce9d31d4", "target_family": "deontic", "target_probability": 0.081921366012}`
  evidence: `{"family_margin": -0.985718020706, "hint_id": "modal-synthesis-bb658cca3176e25c", "predicted_family": "frame", "priority": 0.998186591319, "sample_id": "us-code-10-908a-fbe6c38f28cfd606", "target_family": "conditional_normative", "target_probability": 0.001813408681}`
- `program-0fc88493970a0230` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-fff7763164907c54` score `0.974603`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.261725704988, "hint_id": "modal-synthesis-38bbf6f90bdac9e9", "predicted_family": "conditional_normative", "priority": 0.847681736108, "sample_id": "us-code-30-937-f058702f2785ed46", "target_family": "temporal", "target_probability": 0.152318263892}`
  evidence: `{"family_margin": -0.877970506123, "hint_id": "modal-synthesis-9384bf659793061e", "predicted_family": "conditional_normative", "priority": 0.999892097996, "sample_id": "us-code-42-1395xx.-c2992ed073329710", "target_family": "deontic", "target_probability": 0.000107902004}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-dfb8ba0956eb6ac1", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-42-628a.-55b4902894e86925", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": -0.965909998548, "hint_id": "modal-synthesis-e42f9235b7238c35", "predicted_family": "conditional_normative", "priority": 0.998208642478, "sample_id": "us-code-20-1103-320b576a1fbcb972", "target_family": "deontic", "target_probability": 0.001791357522}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
