# packet-000028

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000028/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000028/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000028-20260519_122139

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-da3192c3055a944d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-da3192c3055a944d` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.046351027126, "hint_id": "modal-synthesis-07913e5b8ff6d18e", "predicted_family": "deontic", "priority": 0.721893837244, "sample_id": "us-code-22-7707-cdc74b8d1b080e59", "target_family": "temporal", "target_probability": 0.278106162756}`
  evidence: `{"family_margin": -0.447743270967, "hint_id": "modal-synthesis-6fd85952e88d79aa", "predicted_family": "conditional_normative", "priority": 0.813440303764, "sample_id": "us-code-22-801-5e460b92fcea13cc", "target_family": "temporal", "target_probability": 0.186559696236}`
  evidence: `{"family_margin": -0.565158419096, "hint_id": "modal-synthesis-cc12bef224da2804", "predicted_family": "deontic", "priority": 0.950474057984, "sample_id": "us-code-12-338-e9f61eb9e13a678a", "target_family": "temporal", "target_probability": 0.049525942016}`
  evidence: `{"family_margin": -0.999373752102, "hint_id": "modal-synthesis-e9988cb9157dfe8b", "predicted_family": "frame", "priority": 0.999908624669, "sample_id": "us-code-1-113-cd403ab39cd45f1c", "target_family": "temporal", "target_probability": 9.1375331e-05}`
- `program-2380152b1f4e4cff` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-da3192c3055a944d` score `0.975418`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.136085692421, "hint_id": "modal-synthesis-0199a96a33dc599d", "predicted_family": "deontic", "priority": 0.727828615158, "sample_id": "us-code-16-460uu-43-fb997cc1fd28fc71", "target_family": "conditional_normative", "target_probability": 0.272171384842}`
  evidence: `{"family_margin": -0.731688096648, "hint_id": "modal-synthesis-2ddfbf9ae42e18e4", "predicted_family": "frame", "priority": 0.956484107946, "sample_id": "us-code-50-47c.-dad134a96a1b873e", "target_family": "conditional_normative", "target_probability": 0.043515892054}`
  evidence: `{"family_margin": 0.128767093112, "hint_id": "modal-synthesis-e78ac69ffa173d3a", "predicted_family": "deontic", "priority": 0.52630037146, "sample_id": "us-code-10-9414b-072e75b5332bc57b", "target_family": "deontic", "target_probability": 0.47369962854}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
