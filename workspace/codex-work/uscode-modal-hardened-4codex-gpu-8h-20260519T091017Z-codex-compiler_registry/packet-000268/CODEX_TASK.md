# packet-000268

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000268/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000268/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000268-20260519_154633

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-b01fbaf4d0b6d092` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b01fbaf4d0b6d092` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.970679750509, "hint_id": "modal-synthesis-0f2d7102b6ed3a3d", "predicted_family": "frame", "priority": 0.996421931426, "sample_id": "us-code-22-1354-6747db394be7d16a", "target_family": "temporal", "target_probability": 0.003578068574}`
  evidence: `{"family_margin": -0.921643636648, "hint_id": "modal-synthesis-2fd68178ef372c79", "predicted_family": "frame", "priority": 0.97154495939, "sample_id": "us-code-42-5844.-0a161e6c2d8d9e38", "target_family": "deontic", "target_probability": 0.02845504061}`
  evidence: `{"family_margin": -0.785893947088, "hint_id": "modal-synthesis-60b874b27616f6bd", "predicted_family": "frame", "priority": 0.912427237685, "sample_id": "us-code-2-194b-c95de1cc8c49a0e9", "target_family": "conditional_normative", "target_probability": 0.087572762315}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a3a932aaa805a657", "predicted_family": "temporal", "priority": 0.650352258125, "sample_id": "us-code-20-1059b-743ed93e96671aec", "target_family": "deontic", "target_probability": 0.349647741875}`
- `program-fc8e4948ae342a83` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b01fbaf4d0b6d092` score `0.972025`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-2da155551dbc495b", "predicted_family": "frame", "priority": 0.943149448469, "sample_id": "us-code-8-1186-866b0788007b45ad", "target_family": "temporal", "target_probability": 0.056850551531}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-6f4085426babaced", "predicted_family": "temporal", "priority": 0.576518842273, "sample_id": "us-code-13-184-f64c50d8f2db025c", "target_family": "conditional_normative", "target_probability": 0.423481157727}`
  evidence: `{"family_margin": -0.628952442126, "hint_id": "modal-synthesis-9433fd925082cf45", "predicted_family": "frame", "priority": 0.982331920334, "sample_id": "us-code-43-737.-159ba480db3e5864", "target_family": "temporal", "target_probability": 0.017668079666}`
  evidence: `{"family_margin": -0.979274746583, "hint_id": "modal-synthesis-ee5d697b81d135ae", "predicted_family": "frame", "priority": 0.991996664484, "sample_id": "us-code-49-14705.-ce33e074ffa4430f", "target_family": "temporal", "target_probability": 0.008003335516}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
