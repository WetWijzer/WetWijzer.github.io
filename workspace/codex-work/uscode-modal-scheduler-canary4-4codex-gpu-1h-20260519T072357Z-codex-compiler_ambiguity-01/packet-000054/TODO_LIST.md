# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-8516a3c075a43559`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8516a3c075a43559` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.815415630013`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-21-301-5c6041ea0606b416, us-code-16-1011-3904d048740cdb51, us-code-18-3528-de588bcb29c3c29c`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-74e0af0590b01663", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-18-3528-de588bcb29c3c29c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.996246890038, "hint_id": "modal-synthesis-8bdb8e38791f7eb3", "predicted_family": "frame", "priority": 1.146246890038, "sample_id": "us-code-16-1011-3904d048740cdb51", "target_family": "temporal"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-bcaf348ef5b97aa6", "predicted_family": "alethic", "priority": 1.15, "sample_id": "us-code-21-301-5c6041ea0606b416", "target_family": "deontic"}`
- `program-7e9808d126d246cc`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8516a3c075a43559` score `0.981627`
  loss: `autoencoder_residual_cluster` = `0.748577915312`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-831-fbe15f1f8d8eafb3, us-code-22-2083-30f65b26f389e617, us-code-26-6424-db6ea190a8ff359f`
  evidence: `{"family_margin": -0.941192519958, "hint_id": "modal-synthesis-2d6e8f814cb15512", "predicted_family": "frame", "priority": 1.091192519958, "sample_id": "us-code-22-2083-30f65b26f389e617", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999208624451, "hint_id": "modal-synthesis-3430e91aa2d494cd", "predicted_family": "frame", "priority": 1.149208624451, "sample_id": "us-code-18-831-fbe15f1f8d8eafb3", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.144667398472, "hint_id": "modal-synthesis-d1f734b108011882", "predicted_family": "temporal", "priority": 0.005332601528, "sample_id": "us-code-26-6424-db6ea190a8ff359f", "target_family": "temporal"}`
- `program-143c1f4ebd6fe17d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-8516a3c075a43559` score `0.95968`
  loss: `autoencoder_residual_cluster` = `0.666612353419`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-4210-84a1442bd9c70a2c, us-code-25-1680p-0f3db7fd6700af7f, us-code-16-552a-5158b7b4f84afb51, us-code-20-78a-e776385e2a7fe165`
  evidence: `{"family_margin": -0.277597579055, "hint_id": "modal-synthesis-39705539a9794996", "predicted_family": "deontic", "priority": 0.427597579055, "sample_id": "us-code-20-78a-e776385e2a7fe165", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.284750434111, "hint_id": "modal-synthesis-9b7acfd7f5c3e418", "predicted_family": "frame", "priority": 0.434750434111, "sample_id": "us-code-16-552a-5158b7b4f84afb51", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-a3489bc0a386d5a0", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-25-1680p-0f3db7fd6700af7f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.985555718125, "hint_id": "modal-synthesis-c9b1405ba25bbb83", "predicted_family": "frame", "priority": 1.135555718125, "sample_id": "us-code-22-4210-84a1442bd9c70a2c", "target_family": "deontic"}`
