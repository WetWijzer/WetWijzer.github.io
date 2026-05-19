# packet-000033

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000033/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000033/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000033-20260519_105025

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a92bea71aba6a6a8` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.980961027656, "hint_id": "modal-synthesis-23971c2e3c6f1c93", "predicted_family": "frame", "priority": 1.130961027656, "sample_id": "us-code-12-1701h-04e1fb99bf8877db", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.967469936232, "hint_id": "modal-synthesis-5899593d4a0f0c00", "predicted_family": "frame", "priority": 1.117469936232, "sample_id": "us-code-16-1701-cabc6adc613cd286", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.687134054969, "hint_id": "modal-synthesis-7764bb7cd79fae08", "predicted_family": "deontic", "priority": 0.837134054969, "sample_id": "us-code-47-1725.-abc549b16337344d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.935627725057, "hint_id": "modal-synthesis-9cdb374ca386b767", "predicted_family": "frame", "priority": 1.085627725057, "sample_id": "us-code-16-3812-451810cfb3a10ab2", "target_family": "temporal"}`
- `program-b5b95544713284db` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `0.968961`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.764480623882, "hint_id": "modal-synthesis-b1fd62daca833937", "predicted_family": "frame", "priority": 0.914480623882, "sample_id": "us-code-42-16395.-8c3254009799e102", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.572728998217, "hint_id": "modal-synthesis-c6841b5396120adb", "predicted_family": "temporal", "priority": 0.722728998217, "sample_id": "us-code-30-1714-dfe0069fa245799f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.979801629208, "hint_id": "modal-synthesis-fb12fe915bc7417d", "predicted_family": "frame", "priority": 1.129801629208, "sample_id": "us-code-42-2164.-c02ebd529bffa982", "target_family": "temporal"}`
- `program-ef1f5b0e544acbf3` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `0.964848`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.630382580416, "hint_id": "modal-synthesis-be572d21a48a87ad", "predicted_family": "alethic", "priority": 0.780382580416, "sample_id": "us-code-47-155.-ae12b5c9c9490b18", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-d5abce1f31887dc5", "predicted_family": "frame", "priority": 0.562883618814, "sample_id": "us-code-16-794-0fe8a57c1c1fd116", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.395294504623, "hint_id": "modal-synthesis-fad11960a16619ea", "predicted_family": "deontic", "priority": 0.545294504623, "sample_id": "us-code-42-1996.-22a4e543fe03ffb6", "target_family": "temporal"}`

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
- `program-a92bea71aba6a6a8`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.042798185979`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1701h-04e1fb99bf8877db, us-code-16-1701-cabc6adc613cd286, us-code-16-3812-451810cfb3a10ab2, us-code-47-1725.-abc549b16337344d`
  evidence: `{"family_margin": -0.980961027656, "hint_id": "modal-synthesis-23971c2e3c6f1c93", "predicted_family": "frame", "priority": 1.130961027656, "sample_id": "us-code-12-1701h-04e1fb99bf8877db", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.967469936232, "hint_id": "modal-synthesis-5899593d4a0f0c00", "predicted_family": "frame", "priority": 1.117469936232, "sample_id": "us-code-16-1701-cabc6adc613cd286", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.687134054969, "hint_id": "modal-synthesis-7764bb7cd79fae08", "predicted_family": "deontic", "priority": 0.837134054969, "sample_id": "us-code-47-1725.-abc549b16337344d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.935627725057, "hint_id": "modal-synthesis-9cdb374ca386b767", "predicted_family": "frame", "priority": 1.085627725057, "sample_id": "us-code-16-3812-451810cfb3a10ab2", "target_family": "temporal"}`
- `program-b5b95544713284db`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `0.968961`
  loss: `autoencoder_residual_cluster` = `0.922337083769`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-2164.-c02ebd529bffa982, us-code-42-16395.-8c3254009799e102, us-code-30-1714-dfe0069fa245799f`
  evidence: `{"family_margin": -0.764480623882, "hint_id": "modal-synthesis-b1fd62daca833937", "predicted_family": "frame", "priority": 0.914480623882, "sample_id": "us-code-42-16395.-8c3254009799e102", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.572728998217, "hint_id": "modal-synthesis-c6841b5396120adb", "predicted_family": "temporal", "priority": 0.722728998217, "sample_id": "us-code-30-1714-dfe0069fa245799f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.979801629208, "hint_id": "modal-synthesis-fb12fe915bc7417d", "predicted_family": "frame", "priority": 1.129801629208, "sample_id": "us-code-42-2164.-c02ebd529bffa982", "target_family": "temporal"}`
- `program-ef1f5b0e544acbf3`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a92bea71aba6a6a8` score `0.964848`
  loss: `autoencoder_residual_cluster` = `0.629520234618`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-47-155.-ae12b5c9c9490b18, us-code-16-794-0fe8a57c1c1fd116, us-code-42-1996.-22a4e543fe03ffb6`
  evidence: `{"family_margin": -0.630382580416, "hint_id": "modal-synthesis-be572d21a48a87ad", "predicted_family": "alethic", "priority": 0.780382580416, "sample_id": "us-code-47-155.-ae12b5c9c9490b18", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-d5abce1f31887dc5", "predicted_family": "frame", "priority": 0.562883618814, "sample_id": "us-code-16-794-0fe8a57c1c1fd116", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.395294504623, "hint_id": "modal-synthesis-fad11960a16619ea", "predicted_family": "deontic", "priority": 0.545294504623, "sample_id": "us-code-42-1996.-22a4e543fe03ffb6", "target_family": "temporal"}`
