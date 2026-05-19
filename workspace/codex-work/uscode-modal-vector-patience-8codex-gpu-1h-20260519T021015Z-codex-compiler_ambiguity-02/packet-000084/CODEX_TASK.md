# packet-000084

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000084/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000084/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000084-20260519_021727

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-9dae88b284fb8dca` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-90f1302a1008ee78", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-25-564u-3e5f6016c5496413", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-9ec006976f308fef", "predicted_family": "frame", "priority": 0.870554053002, "sample_id": "us-code-18-336-fa27971f56c9178b", "target_family": "deontic"}`
- `program-f63bed7d61012b2a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `0.982101`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.66708163055, "hint_id": "modal-synthesis-6e7d503c63ab0b2b", "predicted_family": "temporal", "priority": 0.81708163055, "sample_id": "us-code-26-1035-b286ae25b6800758", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.164578968256, "hint_id": "modal-synthesis-fdab5eeba1fb0031", "predicted_family": "frame", "priority": 0.314578968256, "sample_id": "us-code-43-25 to 25b.-281e835d4b2de5b0", "target_family": "temporal"}`
- `program-691c6074f6caad2f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9dae88b284fb8dca` score `0.980046`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.617808664044, "hint_id": "modal-synthesis-94f5c4d7395853e2", "predicted_family": "deontic", "priority": 0.767808664044, "sample_id": "us-code-40-6306-aeae94d6d1d8eb01", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.453596737625, "hint_id": "modal-synthesis-f1779e058d433f29", "predicted_family": "conditional_normative", "priority": 0.603596737625, "sample_id": "us-code-16-460ss-5-a29152ca8faf3653", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
