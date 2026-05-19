# packet-000033

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000033/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000033/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000033-20260519_084337

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-49b5f4e02b3b8ccf` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999999978986, "hint_id": "modal-synthesis-253a992416e50dcf", "predicted_family": "temporal", "priority": 0.999999999806, "sample_id": "us-code-46-55601.-050cf2f773a2a467", "target_family": "deontic", "target_probability": 1.94e-10}`
  evidence: `{"family_margin": -0.999627887078, "hint_id": "modal-synthesis-3710803deb9067e9", "predicted_family": "frame", "priority": 0.999908601433, "sample_id": "us-code-46-14306.-ca967fe82ca4b42b", "target_family": "epistemic", "target_probability": 9.1398567e-05}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-dab3d42fcb755ae6", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-7-428-0eedbd792171d56c", "target_family": "temporal", "target_probability": 0.173819074614}`
- `program-b6f47a7dffb48a29` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `0.983031`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.199221055742, "hint_id": "modal-synthesis-511d9d7b189fdc5b", "predicted_family": "frame", "priority": 0.728305167674, "sample_id": "us-code-42-5117aa to 5117aa-9b79308d5d7d47fc", "target_family": "temporal", "target_probability": 0.271694832326}`
  evidence: `{"family_margin": -0.796199259613, "hint_id": "modal-synthesis-71b98671c420ee7c", "predicted_family": "deontic", "priority": 0.942212746697, "sample_id": "us-code-22-10421-88b9bc7813665dc2", "target_family": "dynamic", "target_probability": 0.057787253303}`
  evidence: `{"family_margin": -0.999456079449, "hint_id": "modal-synthesis-8309c2c4d160f64a", "predicted_family": "frame", "priority": 0.999751556604, "sample_id": "us-code-22-2364-b6943513a5a5417e", "target_family": "temporal", "target_probability": 0.000248443396}`
- `program-701c9141e65bb442` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `0.982952`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-2ca418b128b1823c", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-19-1520-16c0e38a324a77a8", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.861081253473, "hint_id": "modal-synthesis-dfb23326445ece6d", "predicted_family": "deontic", "priority": 0.976044664512, "sample_id": "us-code-30-32-c56c570185bd36a1", "target_family": "temporal", "target_probability": 0.023955335488}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-f2900d1b6e14746a", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-2-161-2d13bcf6924f8067", "target_family": "deontic", "target_probability": 0.173819074614}`
- `program-f4a369a724b97ce3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->frame","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `0.979676`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-88c41738b0af81a7", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-42-1432.-930f0dd5c94c76f8", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.999999999992, "hint_id": "modal-synthesis-953c5370268651c8", "predicted_family": "temporal", "priority": 0.999999999999, "sample_id": "us-code-48-1494b.-90d4534259e2d44d", "target_family": "deontic", "target_probability": 1e-12}`
  evidence: `{"family_margin": -0.794037310497, "hint_id": "modal-synthesis-d73e96d8f829b55c", "predicted_family": "frame", "priority": 0.983256711591, "sample_id": "us-code-16-460z-11-d82a1186d5c506ac", "target_family": "temporal", "target_probability": 0.016743288409}`
- `program-7ba32f40802779f0` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `0.973461`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.23754545673, "hint_id": "modal-synthesis-3cf1e57143add1d0", "predicted_family": "conditional_normative", "priority": 0.5281316606, "sample_id": "us-code-19-53-e45dc5de82cf456b", "target_family": "conditional_normative", "target_probability": 0.4718683394}`
  evidence: `{"family_margin": -0.889153440775, "hint_id": "modal-synthesis-6a960b14afe19408", "predicted_family": "frame", "priority": 0.981251066793, "sample_id": "us-code-15-9004-32b8c2a43915f762", "target_family": "temporal", "target_probability": 0.018748933207}`
  evidence: `{"family_margin": -0.990253280993, "hint_id": "modal-synthesis-f8b1b07ebaeaa3ae", "predicted_family": "frame", "priority": 0.996349780508, "sample_id": "us-code-22-254e-a9654f1e4eb12705", "target_family": "deontic", "target_probability": 0.003650219492}`
- `program-f128048fb8aac9dd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-49b5f4e02b3b8ccf` score `0.964773`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.750196392965, "hint_id": "modal-synthesis-2e07f7a87967afac", "predicted_family": "temporal", "priority": 0.902952346877, "sample_id": "us-code-6-609a-150079c952e10074", "target_family": "deontic", "target_probability": 0.097047653123}`
  evidence: `{"family_margin": -0.472985425568, "hint_id": "modal-synthesis-2ef5f8fcb91754fa", "predicted_family": "frame", "priority": 0.756779760805, "sample_id": "us-code-2-2186-d4e6d688fb2a82ea", "target_family": "temporal", "target_probability": 0.243220239195}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-77531c3ca8759160", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-42-3030s-33be9732cb2dba7c", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-a22852018e39f52a", "predicted_family": "frame", "priority": 0.636174567276, "sample_id": "us-code-14-2742-456f60f74aa67e0b", "target_family": "deontic", "target_probability": 0.363825432724}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
