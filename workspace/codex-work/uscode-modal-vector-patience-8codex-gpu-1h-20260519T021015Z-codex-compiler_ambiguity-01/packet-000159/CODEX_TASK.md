# packet-000159

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000159/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000159/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000159-20260519_030302

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-38e345593f151154` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-38e345593f151154` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.987892605306, "hint_id": "modal-synthesis-0e9ab28b0a48fffd", "predicted_family": "frame", "priority": 1.137892605306, "sample_id": "us-code-33-426e-2-b919ed11d816bce4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.633195772991, "hint_id": "modal-synthesis-5b34434a7b0d5100", "predicted_family": "frame", "priority": 0.783195772991, "sample_id": "us-code-42-12205.-338224f3fe27ab0f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999868236549, "hint_id": "modal-synthesis-a122a1840548bf29", "predicted_family": "conditional_normative", "priority": 1.149868236549, "sample_id": "us-code-21-384d-a055ac1e34605f4c", "target_family": "frame"}`
  evidence: `{"family_margin": -0.890644758809, "hint_id": "modal-synthesis-b29d522fd8ed490d", "predicted_family": "frame", "priority": 1.040644758809, "sample_id": "us-code-16-2106a-37788d42d32e6540", "target_family": "deontic"}`
- `program-406fb8933cb37bc0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-38e345593f151154` score `0.990414`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.880747666519, "hint_id": "modal-synthesis-391548b9a5db50e9", "predicted_family": "conditional_normative", "priority": 1.030747666519, "sample_id": "us-code-38-2041-a41440e825097173", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996752739219, "hint_id": "modal-synthesis-8da33092a2cf2dfa", "predicted_family": "frame", "priority": 1.146752739219, "sample_id": "us-code-30-1225-5a56d943575f5c33", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.437686879898, "hint_id": "modal-synthesis-94394c4fd91707ad", "predicted_family": "frame", "priority": 0.587686879898, "sample_id": "us-code-46-30302.-04c48d2f164c22f9", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.997527376778, "hint_id": "modal-synthesis-d09fb70714fe783b", "predicted_family": "conditional_normative", "priority": 1.147527376778, "sample_id": "us-code-16-803-cf03d661428eb56c", "target_family": "deontic"}`
- `program-9385ce086256ec89` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-38e345593f151154` score `0.986111`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.346421351195, "hint_id": "modal-synthesis-09eeb4d2219da2bc", "predicted_family": "conditional_normative", "priority": 0.496421351195, "sample_id": "us-code-43-505a-bd7cb4198a14269c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999758484216, "hint_id": "modal-synthesis-1113e9e006cd886d", "predicted_family": "frame", "priority": 1.149758484216, "sample_id": "us-code-5-4107-bb831aabd5551471", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.705884437863, "hint_id": "modal-synthesis-c9cda37e35dd2bea", "predicted_family": "frame", "priority": 0.855884437863, "sample_id": "us-code-16-7702-17b75bdc34fd1cce", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.258055878833, "hint_id": "modal-synthesis-deff2f651a5c533c", "predicted_family": "temporal", "priority": 0.408055878833, "sample_id": "us-code-15-1679e-b11b66bd0238185c", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
