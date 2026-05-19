# packet-000156

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000156/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000156/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000156-20260519_023649

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-ca60bc32beb0e885` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.990305853512, "hint_id": "modal-synthesis-207d5cf88db611c2", "predicted_family": "conditional_normative", "priority": 1.140305853512, "sample_id": "us-code-16-8463-6556ccc2ee90b2bd", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999997217738, "hint_id": "modal-synthesis-a7962287383214f6", "predicted_family": "conditional_normative", "priority": 1.149997217738, "sample_id": "us-code-7-7b-3-8ae854fe9f3e72d9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996629640808, "hint_id": "modal-synthesis-e5a68eb4a4830010", "predicted_family": "conditional_normative", "priority": 1.146629640808, "sample_id": "us-code-26-894-74fa7b27a39e8036", "target_family": "temporal"}`
- `program-6bc69c5543e56f11` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `0.977347`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.988557778739, "hint_id": "modal-synthesis-5fc7f13b0c374eed", "predicted_family": "frame", "priority": 1.138557778739, "sample_id": "us-code-42-1856e.-b5d3bae319ef5cae", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.945211372516, "hint_id": "modal-synthesis-746b19f514bfc91a", "predicted_family": "conditional_normative", "priority": 1.095211372516, "sample_id": "us-code-42-288-8070914136da917f", "target_family": "deontic"}`
- `program-068e259b4e9df818` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `0.966543`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.542828048963, "hint_id": "modal-synthesis-99c982d61777745a", "predicted_family": "frame", "priority": 0.692828048963, "sample_id": "us-code-12-1735f-19-cf4e11a49208d46c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999632873878, "hint_id": "modal-synthesis-9a7c4b3a0e08173a", "predicted_family": "temporal", "priority": 1.149632873878, "sample_id": "us-code-6-621-3530d5bd78adaaad", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
