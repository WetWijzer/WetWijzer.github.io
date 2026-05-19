# packet-000219

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000219/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000219/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000219-20260519_132807

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-59df8f42a91c0f60` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59df8f42a91c0f60` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.9045986346, "hint_id": "modal-synthesis-0f3cad1855dde519", "predicted_family": "frame", "priority": 1.0545986346, "sample_id": "us-code-50-98h-81e88eb05f5b95c6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.663964931589, "hint_id": "modal-synthesis-e64f753aa22b56e9", "predicted_family": "deontic", "priority": 0.813964931589, "sample_id": "us-code-16-460nnn-72-a7c1871912514db1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.617309325395, "hint_id": "modal-synthesis-f6e12b83d1c4b943", "predicted_family": "frame", "priority": 0.767309325395, "sample_id": "us-code-12-2279a-3-e50f61df5c1d28a1", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
