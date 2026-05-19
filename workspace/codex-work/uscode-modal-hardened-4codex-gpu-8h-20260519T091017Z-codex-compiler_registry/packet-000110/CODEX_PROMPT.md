# packet-000110

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000110/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000110/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000110-20260519_134225

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-87dcd347fda577e4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999281017791, "hint_id": "modal-synthesis-68d20ad1f789d621", "predicted_family": "frame", "priority": 0.999854427698, "sample_id": "us-code-38-4301-f41e0787fba53b0a", "target_family": "temporal", "target_probability": 0.000145572302}`
  evidence: `{"family_margin": -0.54822096945, "hint_id": "modal-synthesis-b814fc5078089693", "predicted_family": "frame", "priority": 0.91824018572, "sample_id": "us-code-42-1772.-026fbcdf892256fb", "target_family": "temporal", "target_probability": 0.08175981428}`
  evidence: `{"family_margin": -0.889025829822, "hint_id": "modal-synthesis-ff93adfaac7f6af7", "predicted_family": "epistemic", "priority": 0.998544599729, "sample_id": "us-code-42-7511b.-1d3299a1a442c3ed", "target_family": "temporal", "target_probability": 0.001455400271}`
- `program-0e871ce91c0a506f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->temporal","epistemic->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `0.976312`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.401314129159, "hint_id": "modal-synthesis-47e2c4819483de74", "predicted_family": "alethic", "priority": 0.766444524692, "sample_id": "us-code-7-1944-a2b9c9eaeacf5bf7", "target_family": "deontic", "target_probability": 0.233555475308}`
  evidence: `{"family_margin": -0.190822095789, "hint_id": "modal-synthesis-99db8753167a0ba6", "predicted_family": "deontic", "priority": 0.618355808422, "sample_id": "us-code-22-2734f-015697e8ac5bf2ec", "target_family": "temporal", "target_probability": 0.381644191578}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-c415000adf62dd28", "predicted_family": "epistemic", "priority": 0.69846162364, "sample_id": "us-code-16-2901-9eff43d26a124a28", "target_family": "epistemic", "target_probability": 0.30153837636}`
- `program-d5193ed3c33bddd2` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `0.951939`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.166124058547, "hint_id": "modal-synthesis-c0a706a07375d08d", "predicted_family": "conditional_normative", "priority": 0.577796688236, "sample_id": "us-code-26-6115-9af2f90813f9bed2", "target_family": "conditional_normative", "target_probability": 0.422203311764}`
  evidence: `{"family_margin": -0.988779073937, "hint_id": "modal-synthesis-e778d12119e49e67", "predicted_family": "frame", "priority": 0.995942503862, "sample_id": "us-code-22-1321-9594face20869d3c", "target_family": "conditional_normative", "target_probability": 0.004057496138}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.


## Execution Instructions
Work only inside the packet worktree.
Your worktree edits may be applied back to the source checkout and validated automatically when this packet finishes.
Do not create changes.patch or other patch artifact files; leave source and test edits directly in the worktree.
Treat the packet's program_synthesis_scope metadata as the AST/write-scope boundary; keep edits inside that lane unless a test requires a small adjacent change.
When multiple TODOs are present, treat their semantic_bundle_key or vector_bundle metadata as evidence for one generalized compiler/decompiler/frame improvement over one-off sample fixes.
Implement a narrow deterministic parser, IR, decoder, or frame-logic improvement for the claimed TODOs.
Prefer explainable compiler/decompiler code over learned weights when the TODO concerns modal or frame semantics.
Use local repository files and tests only; do not use web search for this packet.
Run the smallest relevant tests you can before finishing.
Leave unrelated files alone.

## Claimed Autoencoder TODO List
# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-87dcd347fda577e4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.972213071049`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-4301-f41e0787fba53b0a, us-code-42-7511b.-1d3299a1a442c3ed, us-code-42-1772.-026fbcdf892256fb`
  evidence: `{"family_margin": -0.999281017791, "hint_id": "modal-synthesis-68d20ad1f789d621", "predicted_family": "frame", "priority": 0.999854427698, "sample_id": "us-code-38-4301-f41e0787fba53b0a", "target_family": "temporal", "target_probability": 0.000145572302}`
  evidence: `{"family_margin": -0.54822096945, "hint_id": "modal-synthesis-b814fc5078089693", "predicted_family": "frame", "priority": 0.91824018572, "sample_id": "us-code-42-1772.-026fbcdf892256fb", "target_family": "temporal", "target_probability": 0.08175981428}`
  evidence: `{"family_margin": -0.889025829822, "hint_id": "modal-synthesis-ff93adfaac7f6af7", "predicted_family": "epistemic", "priority": 0.998544599729, "sample_id": "us-code-42-7511b.-1d3299a1a442c3ed", "target_family": "temporal", "target_probability": 0.001455400271}`
- `program-0e871ce91c0a506f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->temporal","epistemic->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `0.976312`
  loss: `autoencoder_residual_cluster` = `0.694420652251`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-1944-a2b9c9eaeacf5bf7, us-code-16-2901-9eff43d26a124a28, us-code-22-2734f-015697e8ac5bf2ec`
  evidence: `{"family_margin": -0.401314129159, "hint_id": "modal-synthesis-47e2c4819483de74", "predicted_family": "alethic", "priority": 0.766444524692, "sample_id": "us-code-7-1944-a2b9c9eaeacf5bf7", "target_family": "deontic", "target_probability": 0.233555475308}`
  evidence: `{"family_margin": -0.190822095789, "hint_id": "modal-synthesis-99db8753167a0ba6", "predicted_family": "deontic", "priority": 0.618355808422, "sample_id": "us-code-22-2734f-015697e8ac5bf2ec", "target_family": "temporal", "target_probability": 0.381644191578}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-c415000adf62dd28", "predicted_family": "epistemic", "priority": 0.69846162364, "sample_id": "us-code-16-2901-9eff43d26a124a28", "target_family": "epistemic", "target_probability": 0.30153837636}`
- `program-d5193ed3c33bddd2`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-87dcd347fda577e4` score `0.951939`
  loss: `autoencoder_residual_cluster` = `0.786869596049`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-1321-9594face20869d3c, us-code-26-6115-9af2f90813f9bed2`
  evidence: `{"family_margin": 0.166124058547, "hint_id": "modal-synthesis-c0a706a07375d08d", "predicted_family": "conditional_normative", "priority": 0.577796688236, "sample_id": "us-code-26-6115-9af2f90813f9bed2", "target_family": "conditional_normative", "target_probability": 0.422203311764}`
  evidence: `{"family_margin": -0.988779073937, "hint_id": "modal-synthesis-e778d12119e49e67", "predicted_family": "frame", "priority": 0.995942503862, "sample_id": "us-code-22-1321-9594face20869d3c", "target_family": "conditional_normative", "target_probability": 0.004057496138}`
