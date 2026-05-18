# packet-000238

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000238/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000238/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000238-20260518_194801

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-276b6d75376a3fb0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-276b6d75376a3fb0` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.904857016623, "hint_id": "modal-synthesis-17eb0cae60f9ae84", "predicted_family": "temporal", "priority": 1.054857016623, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.880797076722, "hint_id": "modal-synthesis-267835c7ca3343dd", "predicted_family": "deontic", "priority": 1.030797076722, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.730558609294, "hint_id": "modal-synthesis-560a535b79ebd3ed", "predicted_family": "temporal", "priority": 0.880558609294, "sample_id": "us-code-54-101511.-54b6ccb5549961cf", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999753080179, "hint_id": "modal-synthesis-9324d6490c631c0a", "predicted_family": "temporal", "priority": 1.149753080179, "sample_id": "us-code-38-7310A-219731bd25fca43f", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
