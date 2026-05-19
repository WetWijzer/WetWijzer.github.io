# packet-000111

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000111/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000111/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260519_135222

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-dccd795e75f59ff3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dccd795e75f59ff3` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.968528035805, "hint_id": "modal-synthesis-488851607b3d569b", "predicted_family": "frame", "priority": 0.995141248443, "sample_id": "us-code-15-2706-e7478b73f626b86a", "target_family": "conditional_normative", "target_probability": 0.004858751557}`
  evidence: `{"family_margin": -0.973077580858, "hint_id": "modal-synthesis-562c5edc6f1b407c", "predicted_family": "alethic", "priority": 0.998894303691, "sample_id": "us-code-15-2606-e47cbe28343815cd", "target_family": "deontic", "target_probability": 0.001105696309}`
  evidence: `{"family_margin": -0.566281612036, "hint_id": "modal-synthesis-fd84addad8973dc0", "predicted_family": "frame", "priority": 0.936898807787, "sample_id": "us-code-22-4501-59014ed2366df2b3", "target_family": "epistemic", "target_probability": 0.063101192213}`
- `program-52e4c57fceefc953` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dccd795e75f59ff3` score `0.982928`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.734650522046, "hint_id": "modal-synthesis-0875ee58c7b56751", "predicted_family": "frame", "priority": 0.984508957693, "sample_id": "us-code-14-909-2d64143a7763de74", "target_family": "deontic", "target_probability": 0.015491042307}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-3eff6ef7201f0187", "predicted_family": "conditional_normative", "priority": 0.50390312837, "sample_id": "us-code-16-18e-7283a66843d595f0", "target_family": "conditional_normative", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-caaf4e0a626d4f5d", "predicted_family": "temporal", "priority": 0.559746660672, "sample_id": "us-code-22-1644m-425b496ed9d174bc", "target_family": "temporal", "target_probability": 0.440253339328}`
- `program-3f67e4095cf9841f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dccd795e75f59ff3` score `0.973914`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.466504775746, "hint_id": "modal-synthesis-0c1ec13fc0ec5c8d", "predicted_family": "deontic", "priority": 0.894849975832, "sample_id": "us-code-7-2204-1-a7600025feaa7257", "target_family": "conditional_normative", "target_probability": 0.105150024168}`
  evidence: `{"family_margin": -0.361731958539, "hint_id": "modal-synthesis-25ccd6512eb6821a", "predicted_family": "frame", "priority": 0.841119326986, "sample_id": "us-code-16-410ffff-6159e0362fe1c765", "target_family": "conditional_normative", "target_probability": 0.158880673014}`
  evidence: `{"family_margin": -0.338575202254, "hint_id": "modal-synthesis-f4863c2824148435", "predicted_family": "conditional_normative", "priority": 0.873034299155, "sample_id": "us-code-7-1581-660a3be3ac2f283f", "target_family": "deontic", "target_probability": 0.126965700845}`
- `program-3dd027aa7e5396f8` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dccd795e75f59ff3` score `0.947416`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": 0.020690475744, "hint_id": "modal-synthesis-0763fa7f8b8be8c7", "predicted_family": "conditional_normative", "priority": 0.675621707958, "sample_id": "us-code-26-6657-c0765ea762d0b78e", "target_family": "conditional_normative", "target_probability": 0.324378292042}`
  evidence: `{"family_margin": -0.993985449933, "hint_id": "modal-synthesis-1baa4e4729d1735c", "predicted_family": "frame", "priority": 0.9985033532, "sample_id": "us-code-31-3532-0095a6f986c4315b", "target_family": "deontic", "target_probability": 0.0014966468}`
  evidence: `{"family_margin": -0.221137073043, "hint_id": "modal-synthesis-40dcba4aaff1b06e", "predicted_family": "conditional_normative", "priority": 0.871303374464, "sample_id": "us-code-16-460u-23-d9f23a62fed74210", "target_family": "deontic", "target_probability": 0.128696625536}`
  evidence: `{"family_margin": -0.374438810688, "hint_id": "modal-synthesis-8b14bb92a254aa7c", "predicted_family": "frame", "priority": 0.761263782833, "sample_id": "us-code-25-3073-35d6a7b03ef32534", "target_family": "deontic", "target_probability": 0.238736217167}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
