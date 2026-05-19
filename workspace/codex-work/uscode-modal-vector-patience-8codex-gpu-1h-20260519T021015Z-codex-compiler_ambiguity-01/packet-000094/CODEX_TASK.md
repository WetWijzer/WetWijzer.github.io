# packet-000094

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000094/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000094/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000094-20260519_023957

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-c94faa04b72c4f2d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c94faa04b72c4f2d` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.641210976056, "hint_id": "modal-synthesis-134ff8138a86a7cd", "predicted_family": "temporal", "priority": 0.791210976056, "sample_id": "us-code-16-459j-8-ed4fbf0da24947d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.905148252615, "hint_id": "modal-synthesis-39ff657913c857b1", "predicted_family": "conditional_normative", "priority": 1.055148252615, "sample_id": "us-code-26-7476-14666158c64390c3", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.995576220956, "hint_id": "modal-synthesis-c65366b05b146ef2", "predicted_family": "conditional_normative", "priority": 1.145576220956, "sample_id": "us-code-43-1747.-b8d5f357b1d91a8e", "target_family": "deontic"}`
- `program-5b138eb85572cd27` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c94faa04b72c4f2d` score `0.985237`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.53334883072, "hint_id": "modal-synthesis-063dd92b2653c1f9", "predicted_family": "conditional_normative", "priority": 0.68334883072, "sample_id": "us-code-16-538a-5ea2c3a516d316aa", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.145299598073, "hint_id": "modal-synthesis-3bfb3f7d5695b41a", "predicted_family": "deontic", "priority": 0.004700401927, "sample_id": "us-code-42-285d-db02943ba9789a11", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997438838502, "hint_id": "modal-synthesis-5299a42d96573267", "predicted_family": "conditional_normative", "priority": 1.147438838502, "sample_id": "us-code-50-3093.-00f06b1f3a2a4241", "target_family": "deontic"}`
- `program-e293c086fa5123d1` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c94faa04b72c4f2d` score `0.951938`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.716265383189, "hint_id": "modal-synthesis-118656e4bed3495d", "predicted_family": "alethic", "priority": 0.866265383189, "sample_id": "us-code-20-1128b-9af9d460afd7ab0f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.816824589024, "hint_id": "modal-synthesis-50252161f5d3bc27", "predicted_family": "frame", "priority": 0.966824589024, "sample_id": "us-code-22-262g-3-4598f33f9ff83e75", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999681881453, "hint_id": "modal-synthesis-9c84c94c1369bad0", "predicted_family": "frame", "priority": 1.149681881453, "sample_id": "us-code-16-460l-32-8496645571674501", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-9d45bbc6c43d8c11", "predicted_family": "frame", "priority": 0.878111222864, "sample_id": "us-code-50-3606.-48486f4a53e6b72a", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
