# packet-000024

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000024/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000024/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000024-20260519_000413

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-1ddb283b2246c677` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.500094313565, "hint_id": "modal-synthesis-0eb8897d093a6894", "predicted_family": "frame", "priority": 0.650094313565, "sample_id": "us-code-2-6618-c0019bb488a37bdd", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999999985, "hint_id": "modal-synthesis-41a28cfac843bcb8", "predicted_family": "deontic", "priority": 1.149999999985, "sample_id": "us-code-19-1623-55dbed701beac8c4", "target_family": "temporal"}`
- `program-8bd377b20c5d3502` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.991194`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.460871051442, "hint_id": "modal-synthesis-1dc43032fd61b542", "predicted_family": "conditional_normative", "priority": 0.610871051442, "sample_id": "us-code-15-2068-96f550da92fa0031", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.148879075705, "hint_id": "modal-synthesis-e7940f0c6264095e", "predicted_family": "frame", "priority": 0.298879075705, "sample_id": "us-code-12-635j-d4055fd8d6fa8eb8", "target_family": "deontic"}`
- `program-5db851b5210c4cab` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.986725`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.842895449086, "hint_id": "modal-synthesis-2428ac74a32d0464", "predicted_family": "frame", "priority": 0.992895449086, "sample_id": "us-code-20-7421-40193c348f272b9b", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.085077099697, "hint_id": "modal-synthesis-46c9872dffa8ed75", "predicted_family": "temporal", "priority": 0.064922900303, "sample_id": "us-code-7-2287-e59d961ff6c1d601", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-5b764b29e526c180", "predicted_family": "deontic", "priority": 0.600804952557, "sample_id": "us-code-12-3756-3abb23438f20afd4", "target_family": "conditional_normative"}`
- `program-cabf5d9ccdaf6f2c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->epistemic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.975697`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.893632049076, "hint_id": "modal-synthesis-5c1cd8cca43a396a", "predicted_family": "alethic", "priority": 1.043632049076, "sample_id": "us-code-42-4851.-e3beec5f0d5875eb", "target_family": "epistemic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-99fabd5e69b951c7", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-19-66-c0f75ec4564c0501", "target_family": "temporal"}`
- `program-b9b4792711c4e12f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.964881`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-257bc754227c8a82", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-42-5841.-ff27bf181f6227ac", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.989970952516, "hint_id": "modal-synthesis-980786acb8408c63", "predicted_family": "frame", "priority": 1.139970952516, "sample_id": "us-code-42-1862n-d77569aa22b1ae2f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.149681949852, "hint_id": "modal-synthesis-f7aa1e21069b1382", "predicted_family": "deontic", "priority": 0.000318050148, "sample_id": "us-code-10-3070-f929a4596538ab5a", "target_family": "deontic"}`

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
- `program-1ddb283b2246c677`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.900047156775`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-19-1623-55dbed701beac8c4, us-code-2-6618-c0019bb488a37bdd`
  evidence: `{"family_margin": -0.500094313565, "hint_id": "modal-synthesis-0eb8897d093a6894", "predicted_family": "frame", "priority": 0.650094313565, "sample_id": "us-code-2-6618-c0019bb488a37bdd", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999999985, "hint_id": "modal-synthesis-41a28cfac843bcb8", "predicted_family": "deontic", "priority": 1.149999999985, "sample_id": "us-code-19-1623-55dbed701beac8c4", "target_family": "temporal"}`
- `program-8bd377b20c5d3502`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.991194`
  loss: `autoencoder_residual_cluster` = `0.454875063574`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-2068-96f550da92fa0031, us-code-12-635j-d4055fd8d6fa8eb8`
  evidence: `{"family_margin": -0.460871051442, "hint_id": "modal-synthesis-1dc43032fd61b542", "predicted_family": "conditional_normative", "priority": 0.610871051442, "sample_id": "us-code-15-2068-96f550da92fa0031", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.148879075705, "hint_id": "modal-synthesis-e7940f0c6264095e", "predicted_family": "frame", "priority": 0.298879075705, "sample_id": "us-code-12-635j-d4055fd8d6fa8eb8", "target_family": "deontic"}`
- `program-5db851b5210c4cab`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.986725`
  loss: `autoencoder_residual_cluster` = `0.552874433982`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-7421-40193c348f272b9b, us-code-12-3756-3abb23438f20afd4, us-code-7-2287-e59d961ff6c1d601`
  evidence: `{"family_margin": -0.842895449086, "hint_id": "modal-synthesis-2428ac74a32d0464", "predicted_family": "frame", "priority": 0.992895449086, "sample_id": "us-code-20-7421-40193c348f272b9b", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.085077099697, "hint_id": "modal-synthesis-46c9872dffa8ed75", "predicted_family": "temporal", "priority": 0.064922900303, "sample_id": "us-code-7-2287-e59d961ff6c1d601", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-5b764b29e526c180", "predicted_family": "deontic", "priority": 0.600804952557, "sample_id": "us-code-12-3756-3abb23438f20afd4", "target_family": "conditional_normative"}`
- `program-cabf5d9ccdaf6f2c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->epistemic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.975697`
  loss: `autoencoder_residual_cluster` = `0.596816024538`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-4851.-e3beec5f0d5875eb, us-code-19-66-c0f75ec4564c0501`
  evidence: `{"family_margin": -0.893632049076, "hint_id": "modal-synthesis-5c1cd8cca43a396a", "predicted_family": "alethic", "priority": 1.043632049076, "sample_id": "us-code-42-4851.-e3beec5f0d5875eb", "target_family": "epistemic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-99fabd5e69b951c7", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-19-66-c0f75ec4564c0501", "target_family": "temporal"}`
- `program-b9b4792711c4e12f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1ddb283b2246c677` score `0.964881`
  loss: `autoencoder_residual_cluster` = `0.763429667555`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-5841.-ff27bf181f6227ac, us-code-42-1862n-d77569aa22b1ae2f, us-code-10-3070-f929a4596538ab5a`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-257bc754227c8a82", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-42-5841.-ff27bf181f6227ac", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.989970952516, "hint_id": "modal-synthesis-980786acb8408c63", "predicted_family": "frame", "priority": 1.139970952516, "sample_id": "us-code-42-1862n-d77569aa22b1ae2f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.149681949852, "hint_id": "modal-synthesis-f7aa1e21069b1382", "predicted_family": "deontic", "priority": 0.000318050148, "sample_id": "us-code-10-3070-f929a4596538ab5a", "target_family": "deontic"}`
