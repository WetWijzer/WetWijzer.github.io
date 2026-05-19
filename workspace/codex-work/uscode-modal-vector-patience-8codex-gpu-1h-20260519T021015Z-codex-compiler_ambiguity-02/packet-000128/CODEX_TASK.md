# packet-000128

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000128/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000128/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000128-20260519_022939

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f4f0529bd4fc673f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","frame->deontic","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4f0529bd4fc673f` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.717202017907, "hint_id": "modal-synthesis-70e45971be02482a", "predicted_family": "conditional_normative", "priority": 0.867202017907, "sample_id": "us-code-20-1234a-c0c9de2e60efc6b2", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-ab37fedd6745e0bc", "predicted_family": "frame", "priority": 0.93969827777, "sample_id": "us-code-30-2005-fb3e3d49bf0e1ddc", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.861810021407, "hint_id": "modal-synthesis-c6d5c25e305a85d4", "predicted_family": "temporal", "priority": 1.011810021407, "sample_id": "us-code-19-58b-d71e91a159ddef89", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999954636578, "hint_id": "modal-synthesis-c73c88a3d61fc55b", "predicted_family": "temporal", "priority": 1.149954636578, "sample_id": "us-code-20-1070d-2-28da4a8db201b083", "target_family": "frame"}`
- `program-a954eb0bae03c64d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4f0529bd4fc673f` score `0.965008`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-51e25b6a21ad7fd3", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-36-20701-06bfdca7ebd52e4e", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.39528005226, "hint_id": "modal-synthesis-6e31a231f044b179", "predicted_family": "deontic", "priority": 0.54528005226, "sample_id": "us-code-16-1423c-ada47c1062b73ed9", "target_family": "frame"}`
  evidence: `{"family_margin": -0.605924338763, "hint_id": "modal-synthesis-b94c6ff0fdfb0bc1", "predicted_family": "frame", "priority": 0.755924338763, "sample_id": "us-code-30-186-07b06415e721dc2e", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
