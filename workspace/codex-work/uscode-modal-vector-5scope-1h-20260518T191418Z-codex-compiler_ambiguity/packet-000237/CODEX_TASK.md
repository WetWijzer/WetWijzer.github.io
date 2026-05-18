# packet-000237

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000237/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000237/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000237-20260518_194304

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-fd49422e1f0d49dc` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fd49422e1f0d49dc` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.732922273587, "hint_id": "modal-synthesis-1cd08223e59ba186", "predicted_family": "deontic", "priority": 0.882922273587, "sample_id": "us-code-5-8464a-7b232fae83466b72", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-28d998e040318161", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-2-1516-e49d03132a8b32ab", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.714386779384, "hint_id": "modal-synthesis-7fef2c1740c5e672", "predicted_family": "deontic", "priority": 0.864386779384, "sample_id": "us-code-7-8758-6c50bb2c1676bbf9", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
