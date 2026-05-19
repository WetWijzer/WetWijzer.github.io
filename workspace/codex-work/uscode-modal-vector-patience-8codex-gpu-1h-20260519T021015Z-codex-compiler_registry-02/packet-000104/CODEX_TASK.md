# packet-000104

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000104/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000104/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000104-20260519_023956

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-7d31f2f33536b56a` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.999681881453, "hint_id": "modal-synthesis-2275ddd60b97169c", "predicted_family": "frame", "priority": 0.999908596496, "sample_id": "us-code-16-460l-32-8496645571674501", "target_family": "conditional_normative", "target_probability": 9.1403504e-05}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-6cc0fa128c6ec69c", "predicted_family": "frame", "priority": 0.918866010745, "sample_id": "us-code-50-3606.-48486f4a53e6b72a", "target_family": "deontic", "target_probability": 0.081133989255}`
  evidence: `{"family_margin": -0.816824589024, "hint_id": "modal-synthesis-d802a5a437785724", "predicted_family": "frame", "priority": 0.919118075131, "sample_id": "us-code-22-262g-3-4598f33f9ff83e75", "target_family": "deontic", "target_probability": 0.080881924869}`
  evidence: `{"family_margin": -0.716265383189, "hint_id": "modal-synthesis-e8ab22f5ee64dc41", "predicted_family": "alethic", "priority": 0.874233033517, "sample_id": "us-code-20-1128b-9af9d460afd7ab0f", "target_family": "deontic", "target_probability": 0.125766966483}`
- `program-47e90120b9995fdd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `0.972648`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.997438838502, "hint_id": "modal-synthesis-01ad7d672fcf2716", "predicted_family": "conditional_normative", "priority": 0.999989320726, "sample_id": "us-code-50-3093.-00f06b1f3a2a4241", "target_family": "deontic", "target_probability": 1.0679274e-05}`
  evidence: `{"family_margin": -0.53334883072, "hint_id": "modal-synthesis-af9b558e39ffd078", "predicted_family": "conditional_normative", "priority": 0.772810010596, "sample_id": "us-code-16-538a-5ea2c3a516d316aa", "target_family": "deontic", "target_probability": 0.227189989404}`
  evidence: `{"family_margin": 0.145299598073, "hint_id": "modal-synthesis-bceab1302fac0410", "predicted_family": "deontic", "priority": 0.553021405916, "sample_id": "us-code-42-285d-db02943ba9789a11", "target_family": "deontic", "target_probability": 0.446978594084}`
- `program-323e244dbaadd2ce` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","conditional_normative->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7d31f2f33536b56a` score `0.955221`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.905148252615, "hint_id": "modal-synthesis-8443446d82f96bc4", "predicted_family": "conditional_normative", "priority": 0.952574126876, "sample_id": "us-code-26-7476-14666158c64390c3", "target_family": "temporal", "target_probability": 0.047425873124}`
  evidence: `{"family_margin": -0.995576220956, "hint_id": "modal-synthesis-c1dc29866843e610", "predicted_family": "conditional_normative", "priority": 0.999683971207, "sample_id": "us-code-43-1747.-b8d5f357b1d91a8e", "target_family": "deontic", "target_probability": 0.000316028793}`
  evidence: `{"family_margin": -0.641210976056, "hint_id": "modal-synthesis-ea0712dd814b247c", "predicted_family": "temporal", "priority": 0.840549686562, "sample_id": "us-code-16-459j-8-ed4fbf0da24947d1", "target_family": "deontic", "target_probability": 0.159450313438}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
