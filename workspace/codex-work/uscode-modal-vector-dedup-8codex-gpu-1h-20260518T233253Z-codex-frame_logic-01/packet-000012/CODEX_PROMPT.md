# packet-000012

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-frame_logic-01/packet-000012/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-frame_logic-01/packet-000012/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-frame_logic-01/worktrees/agent-codex-frame_logic-01-packet-000012-20260518_233406

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-12a974d63aa5b4cc` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-12a974d63aa5b4cc` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"hint_id": "modal-synthesis-4a0ad734cbc378a5", "priority": 0.536204008798, "sample_id": "us-code-12-639-a6faf86b06383bb9"}`
  evidence: `{"hint_id": "modal-synthesis-6becf7271b307880", "priority": 0.38549095266, "sample_id": "us-code-22-127-239ab62aacc72ba4"}`
  evidence: `{"hint_id": "modal-synthesis-7d245fbe2a65c48b", "priority": 0.580793508157, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d"}`
  evidence: `{"hint_id": "modal-synthesis-b27dcf283ad9dad7", "priority": 0.341483437006, "sample_id": "us-code-10-10504-6eab7f295cd6facd"}`

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
- TODO count: `1`

## TODOs
- `program-12a974d63aa5b4cc`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-12a974d63aa5b4cc` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.460992976655`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-49-47126.-2322d39a63b9ba2d, us-code-12-639-a6faf86b06383bb9, us-code-22-127-239ab62aacc72ba4, us-code-10-10504-6eab7f295cd6facd`
  evidence: `{"hint_id": "modal-synthesis-4a0ad734cbc378a5", "priority": 0.536204008798, "sample_id": "us-code-12-639-a6faf86b06383bb9"}`
  evidence: `{"hint_id": "modal-synthesis-6becf7271b307880", "priority": 0.38549095266, "sample_id": "us-code-22-127-239ab62aacc72ba4"}`
  evidence: `{"hint_id": "modal-synthesis-7d245fbe2a65c48b", "priority": 0.580793508157, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d"}`
  evidence: `{"hint_id": "modal-synthesis-b27dcf283ad9dad7", "priority": 0.341483437006, "sample_id": "us-code-10-10504-6eab7f295cd6facd"}`
