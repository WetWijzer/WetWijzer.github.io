# packet-000020

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000020/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000020/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000020-20260518_234129

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-bc7cb347feb748dd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.964360748839, "hint_id": "modal-synthesis-0af7ed520bfe171c", "predicted_family": "frame", "priority": 0.999967564472, "sample_id": "us-code-10-844-e75545e37b61e57f", "target_family": "deontic", "target_probability": 3.2435528e-05}`
  evidence: `{"family_margin": -0.989181960764, "hint_id": "modal-synthesis-5bed9814a59a063e", "predicted_family": "temporal", "priority": 0.999097159525, "sample_id": "us-code-38-4102-c9ded8769ebbd704", "target_family": "deontic", "target_probability": 0.000902840475}`
- `program-ee1578722532ba3e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `0.988032`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.099181399841, "hint_id": "modal-synthesis-97fe866e102a23d7", "predicted_family": "frame", "priority": 0.716510210137, "sample_id": "us-code-42-6978.-7d0a3ee24c7e46bf", "target_family": "deontic", "target_probability": 0.283489789863}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-c70b76c6bc24507f", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-24-80-ef2111043611984c", "target_family": "deontic", "target_probability": 0.49609687163}`
- `program-b8df7def2738cdce` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `0.987162`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.985134070983, "hint_id": "modal-synthesis-297d742ec2f5f244", "predicted_family": "frame", "priority": 0.995057942027, "sample_id": "us-code-49-14103.-3ceb982d686d8535", "target_family": "conditional_normative", "target_probability": 0.004942057973}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-f5f0db0d5a926264", "predicted_family": "temporal", "priority": 0.725667012504, "sample_id": "us-code-29-3205-ced7e5263c5303f7", "target_family": "deontic", "target_probability": 0.274332987496}`
- `program-b1ae0c9922d3723e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `0.984678`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.924885675401, "hint_id": "modal-synthesis-22e92901bb3bf66e", "predicted_family": "frame", "priority": 0.96458091891, "sample_id": "us-code-21-1524-aa19993e5da9d029", "target_family": "deontic", "target_probability": 0.03541908109}`
  evidence: `{"family_margin": -0.980030610883, "hint_id": "modal-synthesis-b58920461e9c91ae", "predicted_family": "deontic", "priority": 0.993351810538, "sample_id": "us-code-26-4974-eb27ca6aad760516", "target_family": "conditional_normative", "target_probability": 0.006648189462}`
- `program-8c27292856db04b7` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `0.981354`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.031508900693, "hint_id": "modal-synthesis-04df571fde022d16", "predicted_family": "frame", "priority": 0.700402912999, "sample_id": "us-code-16-10-1e096a226413d70c", "target_family": "deontic", "target_probability": 0.299597087001}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-66787b78d506a1b6", "predicted_family": "deontic", "priority": 0.650352258125, "sample_id": "us-code-18-225-94b2deec9f016491", "target_family": "deontic", "target_probability": 0.349647741875}`
  evidence: `{"family_margin": -0.493804106414, "hint_id": "modal-synthesis-e749e68d7992f61f", "predicted_family": "deontic", "priority": 0.999996965944, "sample_id": "us-code-25-5614-36b3f84152c54706", "target_family": "temporal", "target_probability": 3.034056e-06}`
- `program-94347b4652031a06` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bc7cb347feb748dd` score `0.980296`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.568315764215, "hint_id": "modal-synthesis-0a45e52143ad7ab2", "predicted_family": "frame", "priority": 0.998954479152, "sample_id": "us-code-26-9010-6370fc87e90c3ae4", "target_family": "temporal", "target_probability": 0.001045520848}`
  evidence: `{"family_margin": -0.845412968046, "hint_id": "modal-synthesis-1d04e670b0f56750", "predicted_family": "frame", "priority": 0.967624376433, "sample_id": "us-code-16-1304-dd61929096427adf", "target_family": "deontic", "target_probability": 0.032375623567}`
  evidence: `{"family_margin": -0.158692188725, "hint_id": "modal-synthesis-2a84b726881eac2b", "predicted_family": "frame", "priority": 0.755376930135, "sample_id": "us-code-42-5116g.-c4c7a3075a77de15", "target_family": "deontic", "target_probability": 0.244623069865}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
