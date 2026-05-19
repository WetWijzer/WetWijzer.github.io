# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-9bf9b3dcb7cff1f9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.006392568348`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-668-be76cc69905bc870, us-code-30-1751-429bbb3228cd7eb2`
  evidence: `{"family_margin": -0.760921047218, "hint_id": "modal-synthesis-97c6a7baba122111", "predicted_family": "deontic", "priority": 0.910921047218, "sample_id": "us-code-30-1751-429bbb3228cd7eb2", "target_family": "frame"}`
  evidence: `{"family_margin": -0.951864089479, "hint_id": "modal-synthesis-f4b74fc4f3c929cb", "predicted_family": "frame", "priority": 1.101864089479, "sample_id": "us-code-10-668-be76cc69905bc870", "target_family": "temporal"}`
- `program-ac28d7baffe84e33`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `0.987569`
  loss: `autoencoder_residual_cluster` = `0.781056711231`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-12333.-d32797690eb1f7a0, us-code-16-430f-1-a0a5ab553335000c`
  evidence: `{"family_margin": -0.457881989941, "hint_id": "modal-synthesis-21df915346578ee3", "predicted_family": "deontic", "priority": 0.607881989941, "sample_id": "us-code-16-430f-1-a0a5ab553335000c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.804231432521, "hint_id": "modal-synthesis-debccc6967e75e23", "predicted_family": "frame", "priority": 0.954231432521, "sample_id": "us-code-42-12333.-d32797690eb1f7a0", "target_family": "deontic"}`
- `program-2493e0cb81951493`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `0.977007`
  loss: `autoencoder_residual_cluster` = `0.801408261175`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-7409-2a69930501e77785, us-code-10-2650-fc88eeb2517632d4, us-code-20-3608-fb6f1608d67075db`
  evidence: `{"family_margin": -0.978102474692, "hint_id": "modal-synthesis-a4926825ace3bdcf", "predicted_family": "frame", "priority": 1.128102474692, "sample_id": "us-code-26-7409-2a69930501e77785", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.976122308832, "hint_id": "modal-synthesis-b849570ced4558e1", "predicted_family": "frame", "priority": 1.126122308832, "sample_id": "us-code-10-2650-fc88eeb2517632d4", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-dd2d671e98ad9e06", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-20-3608-fb6f1608d67075db", "target_family": "deontic"}`
- `program-0b2c780264dcf485`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `0.951864`
  loss: `autoencoder_residual_cluster` = `0.775674673673`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-10201-bb60ff3d29dadc2c, us-code-46-11204.-e662cd03a7926135, us-code-42-8303.-a76959e67b6b69ca`
  evidence: `{"family_margin": -0.856937489542, "hint_id": "modal-synthesis-3190234b8f3aad37", "predicted_family": "frame", "priority": 1.006937489542, "sample_id": "us-code-22-10201-bb60ff3d29dadc2c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.55178270417, "hint_id": "modal-synthesis-9a67497c32738963", "predicted_family": "deontic", "priority": 0.70178270417, "sample_id": "us-code-46-11204.-e662cd03a7926135", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.468303827307, "hint_id": "modal-synthesis-f69b878f6d574ad5", "predicted_family": "frame", "priority": 0.618303827307, "sample_id": "us-code-42-8303.-a76959e67b6b69ca", "target_family": "deontic"}`
- `program-fb5ce21654e207f5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `0.935725`
  loss: `autoencoder_residual_cluster` = `0.889985128098`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-3942-60a29efa67206b9d, us-code-18-797-9f95397c66584e64, us-code-19-1436-03f836d62061219f, us-code-22-1644k-198b937dc7e81677`
  evidence: `{"family_margin": -0.999156828816, "hint_id": "modal-synthesis-98293bf1cd3d2dd0", "predicted_family": "frame", "priority": 1.149156828816, "sample_id": "us-code-22-3942-60a29efa67206b9d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.962915743756, "hint_id": "modal-synthesis-bb2fb57988f9ef50", "predicted_family": "frame", "priority": 1.112915743756, "sample_id": "us-code-19-1436-03f836d62061219f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-d68fce43acb3931a", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-22-1644k-198b937dc7e81677", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997867939822, "hint_id": "modal-synthesis-ffa22266bdb14c19", "predicted_family": "frame", "priority": 1.147867939822, "sample_id": "us-code-18-797-9f95397c66584e64", "target_family": "temporal"}`
- `program-e5eafa867f2522bb`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9bf9b3dcb7cff1f9` score `0.913635`
  loss: `autoencoder_residual_cluster` = `0.69050351471`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-561-82a2eab5582e6fab, us-code-16-773i-f00163a41a770798, us-code-22-6411-ba89ac9fe511e033, us-code-35-252-fa7caa868816aa81`
  evidence: `{"family_margin": -0.699805562615, "hint_id": "modal-synthesis-3fb8f51d1df6e995", "predicted_family": "alethic", "priority": 0.849805562615, "sample_id": "us-code-16-773i-f00163a41a770798", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.066879344913, "hint_id": "modal-synthesis-66b8fea65c21adbf", "predicted_family": "deontic", "priority": 0.083120655087, "sample_id": "us-code-35-252-fa7caa868816aa81", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.555287419513, "hint_id": "modal-synthesis-fdc60711c561f46e", "predicted_family": "frame", "priority": 0.705287419513, "sample_id": "us-code-22-6411-ba89ac9fe511e033", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.973800421626, "hint_id": "modal-synthesis-ffdab6c0dc8aba0d", "predicted_family": "frame", "priority": 1.123800421626, "sample_id": "us-code-5-561-82a2eab5582e6fab", "target_family": "deontic"}`
