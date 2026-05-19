# packet-000108

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000108/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000108/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000108-20260519_132050

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-41750384f38d600e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","alethic->epistemic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41750384f38d600e` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.601340220277, "hint_id": "modal-synthesis-020c889c92f8dcb0", "predicted_family": "frame", "priority": 0.88568818043, "sample_id": "us-code-7-1637b-770ebbeb9330c4fd", "target_family": "deontic", "target_probability": 0.11431181957}`
  evidence: `{"family_margin": -0.326486646276, "hint_id": "modal-synthesis-08735039fd583b33", "predicted_family": "alethic", "priority": 0.982893504773, "sample_id": "us-code-20-4011-f7a21f791039ec23", "target_family": "epistemic", "target_probability": 0.017106495227}`
  evidence: `{"family_margin": -0.896839706151, "hint_id": "modal-synthesis-6f23b93437cca3ef", "predicted_family": "alethic", "priority": 0.970432922647, "sample_id": "us-code-42-247b-6963b9eb980a0dcf", "target_family": "conditional_normative", "target_probability": 0.029567077353}`
  evidence: `{"family_margin": -0.963149640055, "hint_id": "modal-synthesis-f7d605d628ce4f98", "predicted_family": "frame", "priority": 0.987458333753, "sample_id": "us-code-49-10901.-36145fd5d606aea9", "target_family": "deontic", "target_probability": 0.012541666247}`
- `program-e18ef6b1e40ffae1` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41750384f38d600e` score `0.965331`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.963281367381, "hint_id": "modal-synthesis-44d486380b8cb6c2", "predicted_family": "frame", "priority": 0.985355777756, "sample_id": "us-code-15-6612-47fab61cbad1138a", "target_family": "conditional_normative", "target_probability": 0.014644222244}`
  evidence: `{"family_margin": -0.132081408712, "hint_id": "modal-synthesis-cf644fbe13800694", "predicted_family": "conditional_normative", "priority": 0.779864318813, "sample_id": "us-code-12-4586-94f51ab219e6e58d", "target_family": "deontic", "target_probability": 0.220135681187}`
  evidence: `{"family_margin": -0.823537218695, "hint_id": "modal-synthesis-fa7078dc3849bb02", "predicted_family": "frame", "priority": 0.923637087829, "sample_id": "us-code-16-698n-c9d56fba5f06bc9d", "target_family": "deontic", "target_probability": 0.076362912171}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
