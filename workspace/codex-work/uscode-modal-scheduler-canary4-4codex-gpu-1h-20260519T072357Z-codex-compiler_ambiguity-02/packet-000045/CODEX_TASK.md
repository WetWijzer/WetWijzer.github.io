# packet-000045

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000045/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000045/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000045-20260519_075133

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-de0bea72375a7009` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.794037310497, "hint_id": "modal-synthesis-2d190148e3d9d12f", "predicted_family": "frame", "priority": 0.944037310497, "sample_id": "us-code-16-460z-11-d82a1186d5c506ac", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999999999992, "hint_id": "modal-synthesis-374f73d2555faa2d", "predicted_family": "temporal", "priority": 1.149999999992, "sample_id": "us-code-48-1494b.-90d4534259e2d44d", "target_family": "deontic"}`
- `program-34805b47ee85c1ca` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `0.987965`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.319507045233, "hint_id": "modal-synthesis-782282581c3a525e", "predicted_family": "deontic", "priority": 0.469507045233, "sample_id": "us-code-2-1385-ebbcc5d70fc5a836", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-ba3fdd8ac9a35e19", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-6-321h-83093fb8aa566f6e", "target_family": "deontic"}`
- `program-e935cf93395aecb0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `0.981465`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.861081253473, "hint_id": "modal-synthesis-349ff4c19eb43731", "predicted_family": "deontic", "priority": 1.011081253473, "sample_id": "us-code-30-32-c56c570185bd36a1", "target_family": "temporal"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-49bda2c5c2c69cad", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-19-1520-16c0e38a324a77a8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-a543e7e8c2be66dc", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-2-161-2d13bcf6924f8067", "target_family": "deontic"}`
- `program-ec6b15ef38a970a6` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `0.95918`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.363165125612, "hint_id": "modal-synthesis-0609d92bd528efe2", "predicted_family": "deontic", "priority": 0.513165125612, "sample_id": "us-code-25-380-a7cb3da37ceba607", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999999999846, "hint_id": "modal-synthesis-78e9321bb15fb1d2", "predicted_family": "temporal", "priority": 1.149999999846, "sample_id": "us-code-42-3028.-a48920161b1e7a31", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997555242754, "hint_id": "modal-synthesis-a374f249869f385d", "predicted_family": "frame", "priority": 1.147555242754, "sample_id": "us-code-20-1011f-4582f720da22b8fa", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-ab0d7b37c21d1e0b", "predicted_family": "frame", "priority": 0.982441698483, "sample_id": "us-code-7-136b-83377b73058cb0ad", "target_family": "temporal"}`
- `program-6508dd313fbe984a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `0.941476`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.817558205162, "hint_id": "modal-synthesis-482637b31b1ffa05", "predicted_family": "frame", "priority": 0.967558205162, "sample_id": "us-code-35-296-bcad57f47b9feeb0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.225664315371, "hint_id": "modal-synthesis-57baaf43c30cd7fd", "predicted_family": "frame", "priority": 0.375664315371, "sample_id": "us-code-30-28g-72ebc181d3f28d61", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.837728494862, "hint_id": "modal-synthesis-5a1d213f1d5bef07", "predicted_family": "temporal", "priority": 0.987728494862, "sample_id": "us-code-10-4125-96495929891f5c5a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997251739449, "hint_id": "modal-synthesis-79629f11aa914337", "predicted_family": "frame", "priority": 1.147251739449, "sample_id": "us-code-12-1701n-d5261eaa493e6a84", "target_family": "conditional_normative"}`
- `program-ffe96185ffc14bea` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-de0bea72375a7009` score `0.92369`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.280391421422, "hint_id": "modal-synthesis-2f76d87d4204ddde", "predicted_family": "conditional_normative", "priority": 0.430391421422, "sample_id": "us-code-16-3833-b68faf0c6def287b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.988870748594, "hint_id": "modal-synthesis-6e15d6e15ff678ef", "predicted_family": "frame", "priority": 1.138870748594, "sample_id": "us-code-2-21-9edeb5683a2b3f8c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.335956946585, "hint_id": "modal-synthesis-9427527b9cd79a95", "predicted_family": "temporal", "priority": 0.485956946585, "sample_id": "us-code-35-151-72adf6e9ff23d38b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.093356747094, "hint_id": "modal-synthesis-ddefa4bc643f6e4d", "predicted_family": "deontic", "priority": 0.056643252906, "sample_id": "us-code-7-6613-1098a1c9aba347e1", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
