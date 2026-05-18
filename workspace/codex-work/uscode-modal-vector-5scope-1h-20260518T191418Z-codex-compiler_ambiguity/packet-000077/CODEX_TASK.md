# packet-000077

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000077/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000077/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000077-20260518_192053

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-0f3619466d6d0393` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0f3619466d6d0393` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-089fc5b98e73c642", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-46-30525.-99a6422ab828fa0c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-100a09f68f736c4b", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-48-1422b.-1024d577005506f9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.730997206769, "hint_id": "modal-synthesis-b11365529676c1b4", "predicted_family": "temporal", "priority": 0.880997206769, "sample_id": "us-code-12-59-693f71484c6a9a7a", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
