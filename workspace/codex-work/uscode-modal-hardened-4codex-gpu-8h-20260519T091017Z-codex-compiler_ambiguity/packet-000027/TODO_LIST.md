# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-2ef0975f1321d909`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2ef0975f1321d909` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.827793390572`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-43-485h-325b6dd405014d87, us-code-43-620m.-e9baf8df4beca760, us-code-20-4303-2cfa428f1663e8b5, us-code-49-31302.-a9accdbfcd1e11fa`
  evidence: `{"family_margin": -0.352426852485, "hint_id": "modal-synthesis-16f85e822052159f", "predicted_family": "frame", "priority": 0.502426852485, "sample_id": "us-code-49-31302.-a9accdbfcd1e11fa", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.396670740767, "hint_id": "modal-synthesis-40aab813911eb4e8", "predicted_family": "alethic", "priority": 0.546670740767, "sample_id": "us-code-20-4303-2cfa428f1663e8b5", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.974579480022, "hint_id": "modal-synthesis-d213b4799b1f330e", "predicted_family": "frame", "priority": 1.124579480022, "sample_id": "us-code-43-620m.-e9baf8df4beca760", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.987496489013, "hint_id": "modal-synthesis-f423fa44666c1f15", "predicted_family": "frame", "priority": 1.137496489013, "sample_id": "us-code-43-485h-325b6dd405014d87", "target_family": "temporal"}`
- `program-91d2543a5062a6c5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->dynamic","frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2ef0975f1321d909` score `0.980928`
  loss: `autoencoder_residual_cluster` = `0.7467562985`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-34-20921-9a0f066af01b89be, us-code-25-957-752853144a70e787, us-code-19-1508-90626a0f8c754dce, us-code-29-31-84bc08150f2562ea`
  evidence: `{"family_margin": -0.952377179972, "hint_id": "modal-synthesis-1b5df65dcb87aef3", "predicted_family": "frame", "priority": 1.102377179972, "sample_id": "us-code-34-20921-9a0f066af01b89be", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.377630258689, "hint_id": "modal-synthesis-2f793df8157b9087", "predicted_family": "deontic", "priority": 0.527630258689, "sample_id": "us-code-19-1508-90626a0f8c754dce", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.168037952136, "hint_id": "modal-synthesis-5f22bbfd91b25a94", "predicted_family": "temporal", "priority": 0.318037952136, "sample_id": "us-code-29-31-84bc08150f2562ea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.888979803204, "hint_id": "modal-synthesis-c09e823923a39046", "predicted_family": "frame", "priority": 1.038979803204, "sample_id": "us-code-25-957-752853144a70e787", "target_family": "conditional_normative"}`
- `program-561152244b1bead7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2ef0975f1321d909` score `0.969014`
  loss: `autoencoder_residual_cluster` = `0.470520346806`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-638b-e34359f35c9b96bf, us-code-16-110-0cbd53104345b901, us-code-10-949o-432529a5c9aa560d`
  evidence: `{"family_margin": 0.029988464343, "hint_id": "modal-synthesis-2806daf5b7473b84", "predicted_family": "deontic", "priority": 0.120011535657, "sample_id": "us-code-10-949o-432529a5c9aa560d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.99154950476, "hint_id": "modal-synthesis-409283c83563d1c7", "predicted_family": "frame", "priority": 1.14154950476, "sample_id": "us-code-10-638b-e34359f35c9b96bf", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-af31ffc5176babd8", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-16-110-0cbd53104345b901", "target_family": "temporal"}`
- `program-1965f88cb9991cc4`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2ef0975f1321d909` score `0.954077`
  loss: `autoencoder_residual_cluster` = `0.418669641064`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-305.-40aab4775f3afffa, us-code-12-56-fab0eedb9ede87b6, us-code-10-12645-8f8576db76eaf7ac`
  evidence: `{"family_margin": -0.200824950891, "hint_id": "modal-synthesis-8e14bbf2d74dcc08", "predicted_family": "frame", "priority": 0.350824950891, "sample_id": "us-code-12-56-fab0eedb9ede87b6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-97113efac6a0f346", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-42-305.-40aab4775f3afffa", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-fbd4fd1467201653", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-10-12645-8f8576db76eaf7ac", "target_family": "temporal"}`
