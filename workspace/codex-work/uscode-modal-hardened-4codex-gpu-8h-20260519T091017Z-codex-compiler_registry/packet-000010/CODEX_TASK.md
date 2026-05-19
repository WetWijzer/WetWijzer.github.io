# packet-000010

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000010/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000010/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000010-20260519_091117

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-00007f4b0c9438d9` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-00007f4b0c9438d9` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.175919526786, "hint_id": "modal-synthesis-f38481d1369f406c", "predicted_family": "deontic", "priority": 0.560201183035, "sample_id": "us-code-15-4013-b282352ae7d2472d", "target_family": "deontic", "target_probability": 0.439798816965}`
  evidence: `{"family_margin": -0.528079517054, "hint_id": "modal-synthesis-f701427e888a4e20", "predicted_family": "conditional_normative", "priority": 0.995435010002, "sample_id": "us-code-4-121-170a4e23192216c5", "target_family": "frame", "target_probability": 0.004564989998}`
- `program-74d7b20cc06e0b12` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-00007f4b0c9438d9` score `0.980926`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-26089b78405fe36e", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-16-198a-69c109aec60f214a", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.706858138788, "hint_id": "modal-synthesis-57b258b987509f58", "predicted_family": "deontic", "priority": 0.997528358164, "sample_id": "us-code-22-1642e-0a4a6e0aa906f829", "target_family": "frame", "target_probability": 0.002471641836}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
