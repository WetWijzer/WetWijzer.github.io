# packet-000181

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000181/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000181/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000181-20260519_145623

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-1d7c7b63b86efff4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1d7c7b63b86efff4` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.988780738882, "hint_id": "modal-synthesis-63397fdd094905b0", "predicted_family": "frame", "priority": 0.996355208515, "sample_id": "us-code-46-3303.-262060b4e52c28d7", "target_family": "conditional_normative", "target_probability": 0.003644791485}`
  evidence: `{"family_margin": -0.360131386457, "hint_id": "modal-synthesis-7ca49c680b49f476", "predicted_family": "alethic", "priority": 0.76161165946, "sample_id": "us-code-50-3533.-fbe9761d5d5aa91b", "target_family": "deontic", "target_probability": 0.23838834054}`
  evidence: `{"family_margin": -0.75246836579, "hint_id": "modal-synthesis-86644f86470af9de", "predicted_family": "deontic", "priority": 0.973649584925, "sample_id": "us-code-2-2182-5a4da71f9b7ed715", "target_family": "temporal", "target_probability": 0.026350415075}`
  evidence: `{"family_margin": -0.914900774437, "hint_id": "modal-synthesis-e158162074edc44e", "predicted_family": "deontic", "priority": 0.974547402, "sample_id": "us-code-43-883.-4cf3c55207a7042d", "target_family": "conditional_normative", "target_probability": 0.025452598}`
- `program-1491268228188532` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1d7c7b63b86efff4` score `0.971899`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-6ad05964012b4b97", "predicted_family": "deontic", "priority": 0.614068880211, "sample_id": "us-code-33-4263-53178b47b118c70f", "target_family": "deontic", "target_probability": 0.385931119789}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-90a0e73f7a68b169", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-20-5121-8e05875a84512b39", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": 0.191143370946, "hint_id": "modal-synthesis-a4424a2fa863d346", "predicted_family": "conditional_normative", "priority": 0.514210253825, "sample_id": "us-code-34-12101-27653168422ea77c", "target_family": "conditional_normative", "target_probability": 0.485789746175}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
