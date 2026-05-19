# packet-000044

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000044/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000044/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000044-20260519_074109

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e236c09be0bc3a87` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e236c09be0bc3a87` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.989259898926, "hint_id": "modal-synthesis-6cbf82962e38787a", "predicted_family": "frame", "priority": 1.139259898926, "sample_id": "us-code-20-5604-e496c6af4f6ffb97", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.952290911916, "hint_id": "modal-synthesis-84d100ce122f838c", "predicted_family": "frame", "priority": 1.102290911916, "sample_id": "us-code-10-7542-3e20c9ff17b7c98f", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.867664184115, "hint_id": "modal-synthesis-c720e19e1e1a7602", "predicted_family": "frame", "priority": 1.017664184115, "sample_id": "us-code-43-957.-45fa418d1d5e2b87", "target_family": "deontic"}`
- `program-cb807d29640df7ec` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e236c09be0bc3a87` score `0.985795`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.928741747566, "hint_id": "modal-synthesis-39b7377355b37afb", "predicted_family": "frame", "priority": 1.078741747566, "sample_id": "us-code-40-15301-89c9da52313b9d58", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.575984669239, "hint_id": "modal-synthesis-498624558fc96c47", "predicted_family": "temporal", "priority": 0.725984669239, "sample_id": "us-code-29-154-7dde92e6219a1637", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.319474751465, "hint_id": "modal-synthesis-67ae3921465362ff", "predicted_family": "temporal", "priority": 0.469474751465, "sample_id": "us-code-18-2515-b7fe0ab6c51e49e0", "target_family": "frame"}`
- `program-ee95df95d2320b6e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e236c09be0bc3a87` score `0.978838`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.837873320286, "hint_id": "modal-synthesis-7323f5bdfcd958ae", "predicted_family": "frame", "priority": 0.987873320286, "sample_id": "us-code-16-833e-30cd9a25a3398f01", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.83015760469, "hint_id": "modal-synthesis-9320e73aa5e956f7", "predicted_family": "temporal", "priority": 0.98015760469, "sample_id": "us-code-16-3931-c4cea8b87c9b66c5", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
