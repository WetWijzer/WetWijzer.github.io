# packet-000037

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000037/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000037/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000037-20260518_225831

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-ebd24ef5e68373aa` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-ebd24ef5e68373aa` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999999999922, "hint_id": "modal-synthesis-64da6f4247a32039", "predicted_family": "deontic", "priority": 0.999999999962, "sample_id": "us-code-18-3523-ca8dbe79c9121836", "target_family": "conditional_normative", "target_probability": 3.8e-11}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-71a1a07fcab74386", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-10-311-44edc8d123967701", "target_family": "frame", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.999997739674, "hint_id": "modal-synthesis-ca3d0089ebb3d08f", "predicted_family": "deontic", "priority": 0.999999999999, "sample_id": "us-code-27-204-58e3ac010eeacfce", "target_family": "temporal", "target_probability": 1e-12}`
- `program-a2d7729c16dda1a0` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-ebd24ef5e68373aa` score `0.99269`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1ebb2b9294baeed5", "predicted_family": "temporal", "priority": 0.621437660869, "sample_id": "us-code-35-302-15247e5e5a144013", "target_family": "deontic", "target_probability": 0.378562339131}`
  evidence: `{"family_margin": -0.463831688409, "hint_id": "modal-synthesis-88ffce62cc32d3c9", "predicted_family": "frame", "priority": 0.82623449314, "sample_id": "us-code-16-3473-d628ecd7a5a5926b", "target_family": "deontic", "target_probability": 0.17376550686}`
  evidence: `{"family_margin": -0.396001780861, "hint_id": "modal-synthesis-b123cc744fb9d74d", "predicted_family": "frame", "priority": 0.851645646711, "sample_id": "us-code-33-3853-72da0bb625fa37b5", "target_family": "conditional_normative", "target_probability": 0.148354353289}`
- `program-240bb85d906080e3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-ebd24ef5e68373aa` score `0.991777`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.998344215132, "hint_id": "modal-synthesis-11aee04245e5450f", "predicted_family": "frame", "priority": 0.999325123867, "sample_id": "us-code-42-1962d-33b9d57c0aa1c276", "target_family": "deontic", "target_probability": 0.000674876133}`
  evidence: `{"family_margin": -0.999995479351, "hint_id": "modal-synthesis-8a8cfc66cbb464db", "predicted_family": "conditional_normative", "priority": 0.999997739676, "sample_id": "us-code-11-547-3b0ef95c5c121efe", "target_family": "temporal", "target_probability": 2.260324e-06}`
  evidence: `{"family_margin": -0.598352142461, "hint_id": "modal-synthesis-b84fa51ae46280d3", "predicted_family": "frame", "priority": 0.997664853849, "sample_id": "us-code-10-10150-2a9db6648ccf9ea4", "target_family": "temporal", "target_probability": 0.002335146151}`
- `program-520d088c35b216ca` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-ebd24ef5e68373aa` score `0.981818`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.772263349992, "hint_id": "modal-synthesis-367e4be51fb31e90", "predicted_family": "frame", "priority": 0.993260303076, "sample_id": "us-code-22-2430-a7c89ee5fb520213", "target_family": "temporal", "target_probability": 0.006739696924}`
  evidence: `{"family_margin": -0.999987782534, "hint_id": "modal-synthesis-55175694cd98c5d3", "predicted_family": "conditional_normative", "priority": 0.999999168481, "sample_id": "us-code-34-12592-82443ae2f01d717b", "target_family": "deontic", "target_probability": 8.31519e-07}`
  evidence: `{"family_margin": -0.879217152154, "hint_id": "modal-synthesis-73962ab47a440d59", "predicted_family": "temporal", "priority": 0.953932804946, "sample_id": "us-code-42-17 to 25e.-be36c9c1c5425f87", "target_family": "conditional_normative", "target_probability": 0.046067195054}`
- `program-fd970b27a8351e4f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-ebd24ef5e68373aa` score `0.980104`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.644460457227, "hint_id": "modal-synthesis-61e574108fb551e5", "predicted_family": "frame", "priority": 0.928187279402, "sample_id": "us-code-22-262p-4c-56831f6deff3c8ac", "target_family": "epistemic", "target_probability": 0.071812720598}`
  evidence: `{"family_margin": -0.990601045781, "hint_id": "modal-synthesis-7afe22984a83d2dd", "predicted_family": "frame", "priority": 0.998177608101, "sample_id": "us-code-48-738.-135a97644c35fe12", "target_family": "deontic", "target_probability": 0.001822391899}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-bae553f1273abd23", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-2-2165-f47062f31de4af78", "target_family": "temporal", "target_probability": 0.008091643722}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
