# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-08f7eb51ea389635`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.988353132365`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-77x-1c3697f7e522de6d, us-code-7-368-b209040cf84318cf, us-code-42-1456 to 1460.-1230df83a3d48e0f`
  evidence: `{"family_margin": -0.993083986751, "hint_id": "modal-synthesis-396997b4978e84d9", "predicted_family": "frame", "priority": 0.998173040276, "sample_id": "us-code-15-77x-1c3697f7e522de6d", "target_family": "temporal", "target_probability": 0.001826959724}`
  evidence: `{"family_margin": -0.923602531686, "hint_id": "modal-synthesis-6d8b83f6afc1361f", "predicted_family": "frame", "priority": 0.971484480007, "sample_id": "us-code-42-1456 to 1460.-1230df83a3d48e0f", "target_family": "conditional_normative", "target_probability": 0.028515519993}`
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-7bafe3bc0f5f8259", "predicted_family": "frame", "priority": 0.995401876812, "sample_id": "us-code-7-368-b209040cf84318cf", "target_family": "temporal", "target_probability": 0.004598123188}`
- `program-351ac2f2cdc11097`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `0.989508`
  loss: `autoencoder_residual_cluster` = `0.808440623618`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-6-321g-944711e1e1604509, us-code-42-14664.-32b9d5a819faf0f3, us-code-10-643-acdbe7fe682498df`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-06a32bd716fa5f26", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-42-14664.-32b9d5a819faf0f3", "target_family": "deontic", "target_probability": 0.168731311045}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1b42d1996e7a1b15", "predicted_family": "temporal", "priority": 0.712640341888, "sample_id": "us-code-10-643-acdbe7fe682498df", "target_family": "temporal", "target_probability": 0.287359658112}`
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-4b1aaeff080ec3e1", "predicted_family": "frame", "priority": 0.881412840012, "sample_id": "us-code-6-321g-944711e1e1604509", "target_family": "conditional_normative", "target_probability": 0.118587159988}`
- `program-94561158f4415591`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `0.98876`
  loss: `autoencoder_residual_cluster` = `0.823136832462`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1507.-1f31a5b1a887defc, us-code-10-1075a-ae9b92ceb649df9c, us-code-16-753-78a54abf676f67c5`
  evidence: `{"family_margin": -0.091944360381, "hint_id": "modal-synthesis-21536bfe12e9d86b", "predicted_family": "conditional_normative", "priority": 0.78546315911, "sample_id": "us-code-10-1075a-ae9b92ceb649df9c", "target_family": "temporal", "target_probability": 0.21453684089}`
  evidence: `{"family_margin": -0.458479155504, "hint_id": "modal-synthesis-3634d415a796528b", "predicted_family": "frame", "priority": 0.764239226327, "sample_id": "us-code-16-753-78a54abf676f67c5", "target_family": "temporal", "target_probability": 0.235760773673}`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-df24a01fe377ade8", "predicted_family": "frame", "priority": 0.91970811195, "sample_id": "us-code-42-1507.-1f31a5b1a887defc", "target_family": "deontic", "target_probability": 0.08029188805}`
- `program-7e96a3b5754f2174`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `0.986389`
  loss: `autoencoder_residual_cluster` = `0.86642413847`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-8107.-9552ff38dc3f163a, us-code-42-254-857b48701ce7bc83, us-code-43-411b.-93317c29bd369fc0`
  evidence: `{"family_margin": -0.146643374542, "hint_id": "modal-synthesis-51ad0351af576377", "predicted_family": "conditional_normative", "priority": 0.82402795055, "sample_id": "us-code-42-254-857b48701ce7bc83", "target_family": "temporal", "target_probability": 0.17597204945}`
  evidence: `{"family_margin": -0.491647274895, "hint_id": "modal-synthesis-8698ca0858383e3b", "predicted_family": "frame", "priority": 0.784057647999, "sample_id": "us-code-43-411b.-93317c29bd369fc0", "target_family": "deontic", "target_probability": 0.215942352001}`
  evidence: `{"family_margin": -0.758607661663, "hint_id": "modal-synthesis-b2318d737031c5d0", "predicted_family": "frame", "priority": 0.991186816862, "sample_id": "us-code-42-8107.-9552ff38dc3f163a", "target_family": "deontic", "target_probability": 0.008813183138}`
- `program-fd28db192fc21858`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `0.98554`
  loss: `autoencoder_residual_cluster` = `0.744077489068`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-305.-40aab4775f3afffa, us-code-10-12645-8f8576db76eaf7ac, us-code-12-56-fab0eedb9ede87b6`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-6afc26bdd93d02e8", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-42-305.-40aab4775f3afffa", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-86e70f38679bf7b2", "predicted_family": "temporal", "priority": 0.720638686515, "sample_id": "us-code-10-12645-8f8576db76eaf7ac", "target_family": "temporal", "target_probability": 0.279361313485}`
  evidence: `{"family_margin": -0.200824950891, "hint_id": "modal-synthesis-8aa867c3bbf0e9bb", "predicted_family": "frame", "priority": 0.685412855304, "sample_id": "us-code-12-56-fab0eedb9ede87b6", "target_family": "deontic", "target_probability": 0.314587144696}`
- `program-1610e7ac14d9a4ce`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08f7eb51ea389635` score `0.977731`
  loss: `autoencoder_residual_cluster` = `0.846931410645`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-29-1191a-03cc45615286dd09, us-code-20-981-aa4698b784bade60, us-code-42-4853.-77710e5c7fd4960a`
  evidence: `{"family_margin": -0.313465632734, "hint_id": "modal-synthesis-0fdecf2a81adf4cf", "predicted_family": "deontic", "priority": 0.686534367266, "sample_id": "us-code-42-4853.-77710e5c7fd4960a", "target_family": "temporal", "target_probability": 0.313465632734}`
  evidence: `{"family_margin": -0.487568741159, "hint_id": "modal-synthesis-65c7c0be8b0abf0c", "predicted_family": "frame", "priority": 0.858248016528, "sample_id": "us-code-20-981-aa4698b784bade60", "target_family": "deontic", "target_probability": 0.141751983472}`
  evidence: `{"family_margin": -0.979955332501, "hint_id": "modal-synthesis-9519cadc192eb109", "predicted_family": "frame", "priority": 0.996011848142, "sample_id": "us-code-29-1191a-03cc45615286dd09", "target_family": "deontic", "target_probability": 0.003988151858}`
