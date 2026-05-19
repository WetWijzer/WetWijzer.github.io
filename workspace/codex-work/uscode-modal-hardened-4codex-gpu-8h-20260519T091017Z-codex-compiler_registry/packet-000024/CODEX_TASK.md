# packet-000024

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000024/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000024/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000024-20260519_114212

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-72c4b67a49ed2be6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-72c4b67a49ed2be6` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.886363126312, "hint_id": "modal-synthesis-0b9a1264821ed92a", "predicted_family": "frame", "priority": 0.978323307868, "sample_id": "us-code-10-2733a-077475dad346b012", "target_family": "temporal", "target_probability": 0.021676692132}`
  evidence: `{"family_margin": -0.871641370684, "hint_id": "modal-synthesis-340ffc9175a4433c", "predicted_family": "frame", "priority": 0.948160627499, "sample_id": "us-code-25-5352-0bba059599ed7867", "target_family": "conditional_normative", "target_probability": 0.051839372501}`
  evidence: `{"family_margin": -0.283228545629, "hint_id": "modal-synthesis-b729045fcf123432", "predicted_family": "deontic", "priority": 0.886269260714, "sample_id": "us-code-16-194-86bb9ee231685cf0", "target_family": "temporal", "target_probability": 0.113730739286}`
  evidence: `{"family_margin": -0.326471773923, "hint_id": "modal-synthesis-d7821ca55f884ebc", "predicted_family": "frame", "priority": 0.856606379567, "sample_id": "us-code-15-4406-06b42cf5db1c97c9", "target_family": "conditional_normative", "target_probability": 0.143393620433}`
- `program-3c7d9be3bde6ca23` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","epistemic->epistemic","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-72c4b67a49ed2be6` score `0.978599`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.844944355229, "hint_id": "modal-synthesis-57c5abb947b75f42", "predicted_family": "frame", "priority": 0.949748386612, "sample_id": "us-code-25-3205-82844da2fd01f148", "target_family": "conditional_normative", "target_probability": 0.050251613388}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-925063038c01b088", "predicted_family": "epistemic", "priority": 0.575389882096, "sample_id": "us-code-38-3601-a493eaa250a21490", "target_family": "epistemic", "target_probability": 0.424610117904}`
  evidence: `{"family_margin": -0.534026866368, "hint_id": "modal-synthesis-af665f2003739b08", "predicted_family": "deontic", "priority": 0.992272285944, "sample_id": "us-code-16-51-a3778f7455c8838c", "target_family": "temporal", "target_probability": 0.007727714056}`
  evidence: `{"family_margin": -0.810658779605, "hint_id": "modal-synthesis-e2aef112ec99216e", "predicted_family": "deontic", "priority": 0.961757682672, "sample_id": "us-code-16-580m-b422f95353b28b31", "target_family": "frame", "target_probability": 0.038242317328}`
- `program-58602448b6073655` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-72c4b67a49ed2be6` score `0.975738`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.979889841698, "hint_id": "modal-synthesis-112eb5137abade14", "predicted_family": "frame", "priority": 0.992663997284, "sample_id": "us-code-28-2201-0190c385b019e533", "target_family": "temporal", "target_probability": 0.007336002716}`
  evidence: `{"family_margin": -0.723804744728, "hint_id": "modal-synthesis-8effa0f0068a813c", "predicted_family": "deontic", "priority": 0.965111546266, "sample_id": "us-code-15-2309-91ab17a0daa24bd1", "target_family": "temporal", "target_probability": 0.034888453734}`
  evidence: `{"family_margin": 0.196156478202, "hint_id": "modal-synthesis-c04ca031fa38de32", "predicted_family": "deontic", "priority": 0.501469471398, "sample_id": "us-code-43-390h-2815ec9e86550e5f", "target_family": "deontic", "target_probability": 0.498530528602}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-cce86952863bab93", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-2-46f-3a8b30575f511c6d", "target_family": "frame", "target_probability": 0.470915888067}`
- `program-7c3466197c705788` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-72c4b67a49ed2be6` score `0.96646`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.976534442234, "hint_id": "modal-synthesis-2a05d8c03dfb0cfd", "predicted_family": "frame", "priority": 0.990152766475, "sample_id": "us-code-16-403i-4fc971cb18a2761e", "target_family": "deontic", "target_probability": 0.009847233525}`
  evidence: `{"family_margin": -0.130920775863, "hint_id": "modal-synthesis-8bcea05190001cff", "predicted_family": "alethic", "priority": 0.635461261372, "sample_id": "us-code-22-277d-46-590d06ce439c2f8c", "target_family": "deontic", "target_probability": 0.364538738628}`
  evidence: `{"family_margin": -0.174240329935, "hint_id": "modal-synthesis-b34fefdb2cc6ff21", "predicted_family": "deontic", "priority": 0.65151934013, "sample_id": "us-code-30-704-7ffdf626721c3d66", "target_family": "conditional_normative", "target_probability": 0.34848065987}`
  evidence: `{"family_margin": -0.986970544558, "hint_id": "modal-synthesis-de1c1d60b9fd1e00", "predicted_family": "frame", "priority": 0.998184287072, "sample_id": "us-code-21-967-19871a230815c843", "target_family": "alethic", "target_probability": 0.001815712928}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
