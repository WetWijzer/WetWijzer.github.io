# packet-000022

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000022/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000022/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000022-20260518_235100

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-d83f66c58fe159eb` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.993949619943, "hint_id": "modal-synthesis-35ca75a7679395e1", "predicted_family": "deontic", "priority": 1.143949619943, "sample_id": "us-code-10-134-4e0c9f58edfe6a64", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.96232754892, "hint_id": "modal-synthesis-55545c03d25ac63c", "predicted_family": "frame", "priority": 1.11232754892, "sample_id": "us-code-16-590n-59122d4701317a4e", "target_family": "temporal"}`
- `program-370d9cced0a11e95` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.993265`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-131d2c8b0a817fc7", "predicted_family": "frame", "priority": 0.359117456717, "sample_id": "us-code-22-262m-1-5f5f95186247fd54", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999937868552, "hint_id": "modal-synthesis-482557691212e980", "predicted_family": "deontic", "priority": 1.149937868552, "sample_id": "us-code-37-302a-4e0eb4cf87987572", "target_family": "temporal"}`
- `program-6ff6f6b8d2ebd36b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.985584`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-35454a28b9691efb", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-43-581 to 586.-52ff80bb1c895f8d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-f2c537dd1ace4b41", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-10-3651-3edc53ba6f53b91a", "target_family": "temporal"}`
- `program-559f7d16b2a910d2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.975483`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999999582303, "hint_id": "modal-synthesis-087898b9b1ba41c0", "predicted_family": "deontic", "priority": 1.149999582303, "sample_id": "us-code-37-307a-bd64425db76c3290", "target_family": "frame"}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-0c074330d38ec483", "predicted_family": "frame", "priority": 0.878111222864, "sample_id": "us-code-2-396-dfc27b68be30b648", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-adf0c09369cb664e", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-42-5654.-da4eaa98895b187f", "target_family": "temporal"}`
- `program-5c602aa7efec8027` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.974024`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-bd44c975e542d88c", "predicted_family": "deontic", "priority": 0.580679318188, "sample_id": "us-code-15-80b-19-2610eb398736664d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-ca6361f3ac9e7b49", "predicted_family": "frame", "priority": 0.19007547842, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative"}`

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

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-d83f66c58fe159eb`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.128138584431`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-134-4e0c9f58edfe6a64, us-code-16-590n-59122d4701317a4e`
  evidence: `{"family_margin": -0.993949619943, "hint_id": "modal-synthesis-35ca75a7679395e1", "predicted_family": "deontic", "priority": 1.143949619943, "sample_id": "us-code-10-134-4e0c9f58edfe6a64", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.96232754892, "hint_id": "modal-synthesis-55545c03d25ac63c", "predicted_family": "frame", "priority": 1.11232754892, "sample_id": "us-code-16-590n-59122d4701317a4e", "target_family": "temporal"}`
- `program-370d9cced0a11e95`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.993265`
  loss: `autoencoder_residual_cluster` = `0.754527662635`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-37-302a-4e0eb4cf87987572, us-code-22-262m-1-5f5f95186247fd54`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-131d2c8b0a817fc7", "predicted_family": "frame", "priority": 0.359117456717, "sample_id": "us-code-22-262m-1-5f5f95186247fd54", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999937868552, "hint_id": "modal-synthesis-482557691212e980", "predicted_family": "deontic", "priority": 1.149937868552, "sample_id": "us-code-37-302a-4e0eb4cf87987572", "target_family": "temporal"}`
- `program-6ff6f6b8d2ebd36b`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.985584`
  loss: `autoencoder_residual_cluster` = `0.872860444444`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-43-581 to 586.-52ff80bb1c895f8d, us-code-10-3651-3edc53ba6f53b91a`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-35454a28b9691efb", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-43-581 to 586.-52ff80bb1c895f8d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-f2c537dd1ace4b41", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-10-3651-3edc53ba6f53b91a", "target_family": "temporal"}`
- `program-559f7d16b2a910d2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.975483`
  loss: `autoencoder_residual_cluster` = `1.035095337224`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-37-307a-bd64425db76c3290, us-code-42-5654.-da4eaa98895b187f, us-code-2-396-dfc27b68be30b648`
  evidence: `{"family_margin": -0.999999582303, "hint_id": "modal-synthesis-087898b9b1ba41c0", "predicted_family": "deontic", "priority": 1.149999582303, "sample_id": "us-code-37-307a-bd64425db76c3290", "target_family": "frame"}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-0c074330d38ec483", "predicted_family": "frame", "priority": 0.878111222864, "sample_id": "us-code-2-396-dfc27b68be30b648", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-adf0c09369cb664e", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-42-5654.-da4eaa98895b187f", "target_family": "temporal"}`
- `program-5c602aa7efec8027`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d83f66c58fe159eb` score `0.974024`
  loss: `autoencoder_residual_cluster` = `0.385377398304`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-80b-19-2610eb398736664d, us-code-20-107e-1-43ac50498bf68122`
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-bd44c975e542d88c", "predicted_family": "deontic", "priority": 0.580679318188, "sample_id": "us-code-15-80b-19-2610eb398736664d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-ca6361f3ac9e7b49", "predicted_family": "frame", "priority": 0.19007547842, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative"}`
