# packet-000179

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000179/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000179/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000179-20260519_143642

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-96d152fbe2532d97` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","deontic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-96d152fbe2532d97` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.655142606276, "hint_id": "modal-synthesis-650373cf664f3273", "predicted_family": "alethic", "priority": 0.995628483351, "sample_id": "us-code-20-1087e-eff08efbdaff3a56", "target_family": "conditional_normative", "target_probability": 0.004371516649}`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-7dd37a6adc34b252", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-36-170506-d2b99e2b9b52b63c", "target_family": "conditional_normative", "target_probability": 0.166643361199}`
  evidence: `{"family_margin": -0.887894843716, "hint_id": "modal-synthesis-9d0a930ca4fae608", "predicted_family": "frame", "priority": 0.963069166268, "sample_id": "us-code-10-10302-92aef49cf32dc7b8", "target_family": "deontic", "target_probability": 0.036930833732}`
  evidence: `{"family_margin": 0.230517106891, "hint_id": "modal-synthesis-dc8135b23667d068", "predicted_family": "deontic", "priority": 0.56778042458, "sample_id": "us-code-42-9117.-5debd34311fd0743", "target_family": "deontic", "target_probability": 0.43221957542}`
- `program-6a86cd6353ad415d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-96d152fbe2532d97` score `0.974995`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.998720258244, "hint_id": "modal-synthesis-8f6829da75d0ad05", "predicted_family": "frame", "priority": 0.999447317755, "sample_id": "us-code-19-1583a-45fe11bde1af14c4", "target_family": "deontic", "target_probability": 0.000552682245}`
  evidence: `{"family_margin": -0.042151771569, "hint_id": "modal-synthesis-9cfda47c0dca6170", "predicted_family": "frame", "priority": 0.599206963866, "sample_id": "us-code-29-1630-3db641f5909e0083", "target_family": "temporal", "target_probability": 0.400793036134}`
  evidence: `{"family_margin": -0.985141882433, "hint_id": "modal-synthesis-bd2836c6f6928e22", "predicted_family": "frame", "priority": 0.997545657196, "sample_id": "us-code-29-633a-a65fadd09e0f26a6", "target_family": "conditional_normative", "target_probability": 0.002454342804}`
  evidence: `{"family_margin": 0.171716803789, "hint_id": "modal-synthesis-e9e78204ac2fd0a0", "predicted_family": "temporal", "priority": 0.640725417958, "sample_id": "us-code-18-3367-34bb7d03d23ec931", "target_family": "temporal", "target_probability": 0.359274582042}`
- `program-b6947a8c3bb83c5b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-96d152fbe2532d97` score `0.953525`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2dbbe03733ce525d", "predicted_family": "deontic", "priority": 0.559746660672, "sample_id": "us-code-15-6410-934e3582cffdc47c", "target_family": "deontic", "target_probability": 0.440253339328}`
  evidence: `{"family_margin": -0.993985449933, "hint_id": "modal-synthesis-7aaebec8d6e7fc71", "predicted_family": "frame", "priority": 0.9985033532, "sample_id": "us-code-22-298-488dd31bd85d3d5d", "target_family": "deontic", "target_probability": 0.0014966468}`
  evidence: `{"family_margin": -0.33982425867, "hint_id": "modal-synthesis-87cffa4241aca799", "predicted_family": "temporal", "priority": 0.946811508084, "sample_id": "us-code-47-334.-69f097820d01d38e", "target_family": "conditional_normative", "target_probability": 0.053188491916}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
