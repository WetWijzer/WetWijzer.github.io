# packet-000026

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000026/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000026/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000026-20260519_120107

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-92e090cf88a4ad81` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","deontic->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-92e090cf88a4ad81` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999999586886, "hint_id": "modal-synthesis-4d9e9176f454e21b", "predicted_family": "alethic", "priority": 0.999999999954, "sample_id": "us-code-28-376-3ca56b96c9476e4b", "target_family": "conditional_normative", "target_probability": 4.6e-11}`
  evidence: `{"family_margin": -0.555974845748, "hint_id": "modal-synthesis-5bd328e9828a6c5e", "predicted_family": "deontic", "priority": 0.997172191539, "sample_id": "us-code-10-2350p-e57d9c10eedfdef1", "target_family": "frame", "target_probability": 0.002827808461}`
- `program-c301b908ccf9d76c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-92e090cf88a4ad81` score `0.948602`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.427971886065, "hint_id": "modal-synthesis-332ec3c66b06b207", "predicted_family": "temporal", "priority": 0.93301484923, "sample_id": "us-code-29-1085b-cffafd0b7cf5d453", "target_family": "deontic", "target_probability": 0.06698515077}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-652d917d44c6a538", "predicted_family": "frame", "priority": 0.943149448469, "sample_id": "us-code-33-466-9e6d8c7abbc26172", "target_family": "temporal", "target_probability": 0.056850551531}`
  evidence: `{"family_margin": -0.268764268861, "hint_id": "modal-synthesis-a21fee46feaf3853", "predicted_family": "frame", "priority": 0.881952791533, "sample_id": "us-code-30-937-f058702f2785ed46", "target_family": "temporal", "target_probability": 0.118047208467}`
  evidence: `{"family_margin": -0.289155588506, "hint_id": "modal-synthesis-c7614c32736fa171", "predicted_family": "deontic", "priority": 0.710844411494, "sample_id": "us-code-20-9706-db957ea3fc5fbd91", "target_family": "temporal", "target_probability": 0.289155588506}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
