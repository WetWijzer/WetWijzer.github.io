# packet-000107

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000107/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000107/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000107-20260519_030924

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e7744bc0bb726d81` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e7744bc0bb726d81` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.997527376778, "hint_id": "modal-synthesis-30de328da173f25d", "predicted_family": "conditional_normative", "priority": 1.0, "sample_id": "us-code-16-803-cf03d661428eb56c", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.880747666519, "hint_id": "modal-synthesis-a11f4e3912758ec3", "predicted_family": "conditional_normative", "priority": 0.999999938278, "sample_id": "us-code-38-2041-a41440e825097173", "target_family": "deontic", "target_probability": 6.1722e-08}`
  evidence: `{"family_margin": -0.996752739219, "hint_id": "modal-synthesis-ab3b91a8d1fd844c", "predicted_family": "frame", "priority": 0.998499186484, "sample_id": "us-code-30-1225-5a56d943575f5c33", "target_family": "deontic", "target_probability": 0.001500813516}`
  evidence: `{"family_margin": -0.437686879898, "hint_id": "modal-synthesis-edda0bf0e9437f75", "predicted_family": "frame", "priority": 0.996180218939, "sample_id": "us-code-46-30302.-04c48d2f164c22f9", "target_family": "temporal", "target_probability": 0.003819781061}`
- `program-a2fd1005e059977b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e7744bc0bb726d81` score `0.989772`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.705884437863, "hint_id": "modal-synthesis-39d1393461fd3274", "predicted_family": "frame", "priority": 0.955931447734, "sample_id": "us-code-16-7702-17b75bdc34fd1cce", "target_family": "deontic", "target_probability": 0.044068552266}`
  evidence: `{"family_margin": -0.346421351195, "hint_id": "modal-synthesis-7a39711d5efc24d2", "predicted_family": "conditional_normative", "priority": 0.798390842842, "sample_id": "us-code-43-505a-bd7cb4198a14269c", "target_family": "temporal", "target_probability": 0.201609157158}`
  evidence: `{"family_margin": -0.258055878833, "hint_id": "modal-synthesis-bdf7dcde1cdeae3c", "predicted_family": "temporal", "priority": 0.695424482452, "sample_id": "us-code-15-1679e-b11b66bd0238185c", "target_family": "deontic", "target_probability": 0.304575517548}`
  evidence: `{"family_margin": -0.999758484216, "hint_id": "modal-synthesis-dabdec59b8ef4cc8", "predicted_family": "frame", "priority": 0.999908589492, "sample_id": "us-code-5-4107-bb831aabd5551471", "target_family": "conditional_normative", "target_probability": 9.1410508e-05}`
- `program-f39c2258dd4b0bbd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e7744bc0bb726d81` score `0.957427`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.265589752753, "hint_id": "modal-synthesis-22214228cedb919f", "predicted_family": "deontic", "priority": 0.845432950315, "sample_id": "us-code-18-119-3c8e7e7e47fc634f", "target_family": "epistemic", "target_probability": 0.154567049685}`
  evidence: `{"family_margin": -0.99999999234, "hint_id": "modal-synthesis-a6afe095110b4b6f", "predicted_family": "temporal", "priority": 0.999999999163, "sample_id": "us-code-2-1902-9bf1dcbf06b93760", "target_family": "deontic", "target_probability": 8.37e-10}`
  evidence: `{"family_margin": -0.975764796208, "hint_id": "modal-synthesis-cd889c2398fa89f9", "predicted_family": "frame", "priority": 0.999688532188, "sample_id": "us-code-16-403c-4-96cbffd14ccb8ab5", "target_family": "temporal", "target_probability": 0.000311467812}`
- `program-7bad35eb059b5633` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e7744bc0bb726d81` score `0.949152`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.964745859147, "hint_id": "modal-synthesis-b231dedeb1e8c687", "predicted_family": "frame", "priority": 0.989252177757, "sample_id": "us-code-42-6341.-175bf33765c9042b", "target_family": "deontic", "target_probability": 0.010747822243}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-c969034b17c382d9", "predicted_family": "frame", "priority": 0.710631513026, "sample_id": "us-code-30-665-75575ae82f97b718", "target_family": "deontic", "target_probability": 0.289368486974}`
  evidence: `{"family_margin": -0.997326341989, "hint_id": "modal-synthesis-ce75ae1e2a5e23ad", "predicted_family": "temporal", "priority": 0.998770866179, "sample_id": "us-code-42-3016.-a01430f068ac3201", "target_family": "frame", "target_probability": 0.001229133821}`
- `program-00a9fe314d60dc40` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","conditional_normative->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e7744bc0bb726d81` score `0.937441`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-3461a098a65c4e3d", "predicted_family": "conditional_normative", "priority": 1.0, "sample_id": "us-code-45-1203.-a58696791a840de6", "target_family": "frame", "target_probability": 0.0}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-5dca671db7d39ebd", "predicted_family": "conditional_normative", "priority": 1.0, "sample_id": "us-code-43-1629c.-fc78c6059bfddd73", "target_family": "deontic", "target_probability": 0.0}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
