# packet-000115

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000115/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000115/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000115-20260518_202257

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-4df0eae96dd0c894` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4df0eae96dd0c894` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.296787504955, "hint_id": "modal-synthesis-231ee99eca5ffc3c", "predicted_family": "deontic", "priority": 0.530489080271, "sample_id": "us-code-46-2104.-968c80c773abaeae", "target_family": "deontic", "target_probability": 0.469510919729}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-97a87b2f12d2967e", "predicted_family": "temporal", "priority": 0.559746660672, "sample_id": "us-code-12-4307-d8adf804365b9891", "target_family": "deontic", "target_probability": 0.440253339328}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
