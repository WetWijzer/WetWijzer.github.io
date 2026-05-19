# packet-000371

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000371/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000371/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000371-20260519_145234

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-593180d41885004e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-593180d41885004e` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.72561328302, "hint_id": "modal-synthesis-3e0cd4ccc5992e2a", "predicted_family": "frame", "priority": 0.87561328302, "sample_id": "us-code-10-8761a-f20006898ff8c3e4", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.667479661137, "hint_id": "modal-synthesis-87507245f24fb37c", "predicted_family": "alethic", "priority": 0.817479661137, "sample_id": "us-code-15-4652-c7d562053cccf08d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.889153440775, "hint_id": "modal-synthesis-e5ece47722242bba", "predicted_family": "frame", "priority": 1.039153440775, "sample_id": "us-code-44-726.-9ba99f9695a05c64", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
