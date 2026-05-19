# packet-000027

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000027/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000027/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000027-20260519_121239

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-dd3befce5c715cd6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dd3befce5c715cd6` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.962984954465, "hint_id": "modal-synthesis-4508fba28f2a5370", "predicted_family": "alethic", "priority": 0.994982639004, "sample_id": "us-code-20-76h-1f1ce11e05701c8d", "target_family": "deontic", "target_probability": 0.005017360996}`
  evidence: `{"family_margin": -0.932971796823, "hint_id": "modal-synthesis-a18433349968e52c", "predicted_family": "frame", "priority": 0.980992422217, "sample_id": "us-code-42-7605.-4569102489e5c30e", "target_family": "temporal", "target_probability": 0.019007577783}`
  evidence: `{"family_margin": -0.481653071989, "hint_id": "modal-synthesis-b11f1d9d91503598", "predicted_family": "frame", "priority": 0.788447322858, "sample_id": "us-code-22-10012-9becbd88b9c27185", "target_family": "temporal", "target_probability": 0.211552677142}`
- `program-6e9682426a44604e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->alethic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dd3befce5c715cd6` score `0.974905`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.352766504081, "hint_id": "modal-synthesis-0d7e36ba000e3a8c", "predicted_family": "deontic", "priority": 0.794698111661, "sample_id": "us-code-22-8903-987f2f8d788186ac", "target_family": "conditional_normative", "target_probability": 0.205301888339}`
  evidence: `{"family_margin": -0.487420205792, "hint_id": "modal-synthesis-6359603283ee7361", "predicted_family": "frame", "priority": 0.817397514594, "sample_id": "us-code-10-1445-2910255cee5ce658", "target_family": "alethic", "target_probability": 0.182602485406}`
- `program-f37d17828e68a04d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->frame","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dd3befce5c715cd6` score `0.973262`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.65648643313, "hint_id": "modal-synthesis-3db4a512e16d53a7", "predicted_family": "deontic", "priority": 0.993287795958, "sample_id": "us-code-20-1097a-38d407570ced3346", "target_family": "frame", "target_probability": 0.006712204042}`
  evidence: `{"family_margin": -0.285743833344, "hint_id": "modal-synthesis-69624405c06c31b5", "predicted_family": "alethic", "priority": 0.768013537106, "sample_id": "us-code-16-799-ed4b744b4bed77ee", "target_family": "deontic", "target_probability": 0.231986462894}`
  evidence: `{"family_margin": -0.800565026919, "hint_id": "modal-synthesis-9e41c1e58ed39bfb", "predicted_family": "frame", "priority": 0.948991488577, "sample_id": "us-code-49-33104.-ca32bd54a404f9ed", "target_family": "conditional_normative", "target_probability": 0.051008511423}`
- `program-94c761ff31caa9be` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","conditional_normative->deontic","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dd3befce5c715cd6` score `0.960734`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.268046389856, "hint_id": "modal-synthesis-14d72cabb8dfb4fe", "predicted_family": "alethic", "priority": 0.717826280902, "sample_id": "us-code-15-2665-22ba978689e710b3", "target_family": "deontic", "target_probability": 0.282173719098}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-1e0aa17e20781914", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-43-33.-107d1990adb411f6", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -0.350189388673, "hint_id": "modal-synthesis-4f5e42c40bf46d31", "predicted_family": "conditional_normative", "priority": 0.796197932799, "sample_id": "us-code-28-540B-9e40f12bc0782de7", "target_family": "deontic", "target_probability": 0.203802067201}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
