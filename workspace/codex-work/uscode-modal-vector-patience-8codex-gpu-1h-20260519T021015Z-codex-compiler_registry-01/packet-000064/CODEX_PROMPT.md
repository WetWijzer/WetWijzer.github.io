# packet-000064

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000064/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000064/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000064-20260519_024350

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-16ce28142eaf2c34` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.948762054016, "hint_id": "modal-synthesis-0ab2639bbf1c1df1", "predicted_family": "conditional_normative", "priority": 0.975948621347, "sample_id": "us-code-38-7361-a13d78c7455475ca", "target_family": "frame", "target_probability": 0.024051378653}`
  evidence: `{"family_margin": -0.992349673205, "hint_id": "modal-synthesis-338a2e590b782270", "predicted_family": "frame", "priority": 0.996342052898, "sample_id": "us-code-7-8321-65577258c00d4c8d", "target_family": "deontic", "target_probability": 0.003657947102}`
- `program-23d8be98a02f03ab` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `0.976644`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999752902114, "hint_id": "modal-synthesis-11a2314e2210e0f4", "predicted_family": "conditional_normative", "priority": 0.999876605462, "sample_id": "us-code-12-2001-2c579d9b8e36ca92", "target_family": "temporal", "target_probability": 0.000123394538}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-25f55c85a37e1342", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-38-4111-6a6fb3e21bf602aa", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.37467147672, "hint_id": "modal-synthesis-a3752f9920375031", "predicted_family": "deontic", "priority": 0.98488639212, "sample_id": "us-code-12-4405-1c8e651c6443dede", "target_family": "temporal", "target_probability": 0.01511360788}`
- `program-ae2272e9d1ac5ac4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `0.932469`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-88324c21945156de", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-28-2345-b875b92e6b07960b", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.98523581034, "hint_id": "modal-synthesis-98eeff3e8002875c", "predicted_family": "frame", "priority": 0.99945477992, "sample_id": "us-code-46-60104.-2c0508c6a33c27c3", "target_family": "temporal", "target_probability": 0.00054522008}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b4b817aaaa2b3a18", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-28-172-9175d654e2f6f6e6", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.608343394737, "hint_id": "modal-synthesis-cc0d2a962788580c", "predicted_family": "temporal", "priority": 0.997285219491, "sample_id": "us-code-42-1862i.-143aec5d69724dc4", "target_family": "deontic", "target_probability": 0.002714780509}`

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

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-16ce28142eaf2c34`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.986145337122`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-8321-65577258c00d4c8d, us-code-38-7361-a13d78c7455475ca`
  evidence: `{"family_margin": -0.948762054016, "hint_id": "modal-synthesis-0ab2639bbf1c1df1", "predicted_family": "conditional_normative", "priority": 0.975948621347, "sample_id": "us-code-38-7361-a13d78c7455475ca", "target_family": "frame", "target_probability": 0.024051378653}`
  evidence: `{"family_margin": -0.992349673205, "hint_id": "modal-synthesis-338a2e590b782270", "predicted_family": "frame", "priority": 0.996342052898, "sample_id": "us-code-7-8321-65577258c00d4c8d", "target_family": "deontic", "target_probability": 0.003657947102}`
- `program-23d8be98a02f03ab`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `0.976644`
  loss: `autoencoder_residual_cluster` = `0.936981307656`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-2001-2c579d9b8e36ca92, us-code-12-4405-1c8e651c6443dede, us-code-38-4111-6a6fb3e21bf602aa`
  evidence: `{"family_margin": -0.999752902114, "hint_id": "modal-synthesis-11a2314e2210e0f4", "predicted_family": "conditional_normative", "priority": 0.999876605462, "sample_id": "us-code-12-2001-2c579d9b8e36ca92", "target_family": "temporal", "target_probability": 0.000123394538}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-25f55c85a37e1342", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-38-4111-6a6fb3e21bf602aa", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.37467147672, "hint_id": "modal-synthesis-a3752f9920375031", "predicted_family": "deontic", "priority": 0.98488639212, "sample_id": "us-code-12-4405-1c8e651c6443dede", "target_family": "temporal", "target_probability": 0.01511360788}`
- `program-ae2272e9d1ac5ac4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-16ce28142eaf2c34` score `0.932469`
  loss: `autoencoder_residual_cluster` = `0.955730231199`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-28-172-9175d654e2f6f6e6, us-code-46-60104.-2c0508c6a33c27c3, us-code-42-1862i.-143aec5d69724dc4, us-code-28-2345-b875b92e6b07960b`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-88324c21945156de", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-28-2345-b875b92e6b07960b", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.98523581034, "hint_id": "modal-synthesis-98eeff3e8002875c", "predicted_family": "frame", "priority": 0.99945477992, "sample_id": "us-code-46-60104.-2c0508c6a33c27c3", "target_family": "temporal", "target_probability": 0.00054522008}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b4b817aaaa2b3a18", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-28-172-9175d654e2f6f6e6", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.608343394737, "hint_id": "modal-synthesis-cc0d2a962788580c", "predicted_family": "temporal", "priority": 0.997285219491, "sample_id": "us-code-42-1862i.-143aec5d69724dc4", "target_family": "deontic", "target_probability": 0.002714780509}`
