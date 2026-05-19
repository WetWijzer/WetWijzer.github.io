# packet-000036

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-launch-diagnostic3-20260519T071948Z-codex-compiler_ambiguity/packet-000036/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-launch-diagnostic3-20260519T071948Z-codex-compiler_ambiguity/packet-000036/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-launch-diagnostic3-20260519T071948Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000036-20260519_072028

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-eb828901adafd41c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-eb828901adafd41c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.024420676493, "hint_id": "modal-synthesis-410272094173acde", "predicted_family": "deontic", "priority": 0.174420676493, "sample_id": "us-code-28-657-46ef5fa4f2d7343c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.225664315371, "hint_id": "modal-synthesis-7a213442ec039763", "predicted_family": "frame", "priority": 0.375664315371, "sample_id": "us-code-28-639-3f6a9bd848b43a0f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.121737687132, "hint_id": "modal-synthesis-9325631464b52155", "predicted_family": "frame", "priority": 0.271737687132, "sample_id": "us-code-42-12623.-3bb0ba584243da4d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.602552306694, "hint_id": "modal-synthesis-a0f159648fb0de75", "predicted_family": "temporal", "priority": 0.752552306694, "sample_id": "us-code-7-3171-25fb9415d0215f89", "target_family": "epistemic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
