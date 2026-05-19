# packet-000045

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_ambiguity-02/packet-000045/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_ambiguity-02/packet-000045/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-packet-smoke-20260519T014817Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000045-20260519_015214

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e309d1d5525500b5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e309d1d5525500b5` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-1309f0344043a8ed", "predicted_family": "frame", "priority": 0.885177285536, "sample_id": "us-code-42-7385.-4f48c347ce9d31d4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.952569757822, "hint_id": "modal-synthesis-76e5245de47551a0", "predicted_family": "conditional_normative", "priority": 1.102569757822, "sample_id": "us-code-10-1141-753a37a225a7b653", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.985718020706, "hint_id": "modal-synthesis-eb24500f072ed3a6", "predicted_family": "frame", "priority": 1.135718020706, "sample_id": "us-code-10-908a-fbe6c38f28cfd606", "target_family": "conditional_normative"}`
- `program-22afcf2c4b9e6623` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e309d1d5525500b5` score `0.974247`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-21805938906b6783", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-42-628a.-55b4902894e86925", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.261725704988, "hint_id": "modal-synthesis-841a041509104fa3", "predicted_family": "conditional_normative", "priority": 0.411725704988, "sample_id": "us-code-30-937-f058702f2785ed46", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.965909998548, "hint_id": "modal-synthesis-e561c58be8d75b3d", "predicted_family": "conditional_normative", "priority": 1.115909998548, "sample_id": "us-code-20-1103-320b576a1fbcb972", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.877970506123, "hint_id": "modal-synthesis-f9d610d7ac1aa033", "predicted_family": "conditional_normative", "priority": 1.027970506123, "sample_id": "us-code-42-1395xx.-c2992ed073329710", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
