# packet-000109

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000109/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000109/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000109-20260519_133207

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-4b8ba2f97fd3af83` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4b8ba2f97fd3af83` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.9045986346, "hint_id": "modal-synthesis-2f302b86ae856ba3", "predicted_family": "frame", "priority": 0.962374393764, "sample_id": "us-code-50-98h-81e88eb05f5b95c6", "target_family": "deontic", "target_probability": 0.037625606236}`
  evidence: `{"family_margin": -0.663964931589, "hint_id": "modal-synthesis-6104c09fec76b40c", "predicted_family": "deontic", "priority": 0.976748854387, "sample_id": "us-code-16-460nnn-72-a7c1871912514db1", "target_family": "epistemic", "target_probability": 0.023251145613}`
  evidence: `{"family_margin": -0.617309325395, "hint_id": "modal-synthesis-f7916b84e3fe9846", "predicted_family": "frame", "priority": 0.88884329073, "sample_id": "us-code-12-2279a-3-e50f61df5c1d28a1", "target_family": "temporal", "target_probability": 0.11115670927}`
- `program-f4675cc81b476265` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4b8ba2f97fd3af83` score `0.960471`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-078cc2a080eee529", "predicted_family": "conditional_normative", "priority": 0.50390312837, "sample_id": "us-code-33-701l-46fcd24a2e0e46c1", "target_family": "conditional_normative", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-6c274f7de03aef0e", "predicted_family": "frame", "priority": 1.0, "sample_id": "us-code-12-1821-af7b05f2f810f8a5", "target_family": "deontic", "target_probability": 0.0}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
