# packet-000039

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000039/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000039/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000039-20260519_021343

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-bf93d2abadb88734` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bf93d2abadb88734` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999324009529, "hint_id": "modal-synthesis-121b1327d734462d", "predicted_family": "frame", "priority": 0.999731044757, "sample_id": "us-code-42-8262g.-4d0259caef5347ae", "target_family": "deontic", "target_probability": 0.000268955243}`
  evidence: `{"family_margin": -0.955200085186, "hint_id": "modal-synthesis-8b823379c5d6218e", "predicted_family": "temporal", "priority": 0.979537142844, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19", "target_family": "deontic", "target_probability": 0.020462857156}`
  evidence: `{"family_margin": -0.918379271216, "hint_id": "modal-synthesis-9b5567f1a1339b0f", "predicted_family": "deontic", "priority": 0.991121619361, "sample_id": "us-code-36-904-23d13763f249af22", "target_family": "temporal", "target_probability": 0.008878380639}`
- `program-637b962baceaf68f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bf93d2abadb88734` score `0.973056`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.99003245694, "hint_id": "modal-synthesis-89e541b7fcb85390", "predicted_family": "frame", "priority": 0.995937360553, "sample_id": "us-code-22-283k-f4ca00d5aa2cbded", "target_family": "deontic", "target_probability": 0.004062639447}`
  evidence: `{"family_margin": -0.516670571692, "hint_id": "modal-synthesis-d05f194ec237fc11", "predicted_family": "frame", "priority": 0.806439434792, "sample_id": "us-code-12-1795i-939576470ce39d47", "target_family": "deontic", "target_probability": 0.193560565208}`
  evidence: `{"family_margin": -0.030428942315, "hint_id": "modal-synthesis-e305f4d67057e09f", "predicted_family": "frame", "priority": 0.710671515739, "sample_id": "us-code-29-1782-0e521bdf6f8f1e1e", "target_family": "deontic", "target_probability": 0.289328484261}`
- `program-8c310267085400c5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bf93d2abadb88734` score `0.951533`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.728575499058, "hint_id": "modal-synthesis-32aeab7729027f15", "predicted_family": "conditional_normative", "priority": 0.885965080322, "sample_id": "us-code-30-878-f6e175862b59fd62", "target_family": "temporal", "target_probability": 0.114034919678}`
  evidence: `{"family_margin": -0.938371183949, "hint_id": "modal-synthesis-bd8c8690583a8280", "predicted_family": "frame", "priority": 0.970781317817, "sample_id": "us-code-28-1873-c9ff189e9971953d", "target_family": "temporal", "target_probability": 0.029218682183}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
