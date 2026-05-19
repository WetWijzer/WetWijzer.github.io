# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-6ef7c7c03fcf6ed2`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.915558379396`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-16183.-128b2c1ba48b8f9d, us-code-42-9605.-e797e44e0150247e, us-code-20-2341-bc423b78c83aa543, us-code-33-59jj-f5897fef9d8e4971`
  evidence: `{"family_margin": -0.201482979004, "hint_id": "modal-synthesis-459ee97630e64fdf", "predicted_family": "frame", "priority": 0.829900630377, "sample_id": "us-code-33-59jj-f5897fef9d8e4971", "target_family": "deontic", "target_probability": 0.170099369623}`
  evidence: `{"family_margin": -0.953447421386, "hint_id": "modal-synthesis-5c8799f8936236ea", "predicted_family": "frame", "priority": 0.992838173126, "sample_id": "us-code-42-9605.-e797e44e0150247e", "target_family": "temporal", "target_probability": 0.007161826874}`
  evidence: `{"family_margin": -0.996957729615, "hint_id": "modal-synthesis-97ac62eccc59f936", "predicted_family": "frame", "priority": 0.999635282247, "sample_id": "us-code-42-16183.-128b2c1ba48b8f9d", "target_family": "conditional_normative", "target_probability": 0.000364717753}`
  evidence: `{"family_margin": -0.364600427884, "hint_id": "modal-synthesis-e167a260bdab9191", "predicted_family": "frame", "priority": 0.839859431836, "sample_id": "us-code-20-2341-bc423b78c83aa543", "target_family": "deontic", "target_probability": 0.160140568164}`
- `program-519853310c40712b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `0.990443`
  loss: `autoencoder_residual_cluster` = `0.824897341445`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-7602-56087c10d6c3e9c5, us-code-26-25E-e44fe00dd7ad0e99, us-code-16-251f-2632856172977771, us-code-42-300j-637b02b85cfdbf2a`
  evidence: `{"family_margin": -0.311277785162, "hint_id": "modal-synthesis-5dfbe0099bdf87d0", "predicted_family": "frame", "priority": 0.863279915326, "sample_id": "us-code-16-251f-2632856172977771", "target_family": "temporal", "target_probability": 0.136720084674}`
  evidence: `{"family_margin": 0.129856995126, "hint_id": "modal-synthesis-7cf07d8b5692afa1", "predicted_family": "deontic", "priority": 0.52229091402, "sample_id": "us-code-42-300j-637b02b85cfdbf2a", "target_family": "deontic", "target_probability": 0.47770908598}`
  evidence: `{"family_margin": -0.773320745828, "hint_id": "modal-synthesis-993b64c7c785a276", "predicted_family": "frame", "priority": 0.918973460641, "sample_id": "us-code-26-25E-e44fe00dd7ad0e99", "target_family": "conditional_normative", "target_probability": 0.081026539359}`
  evidence: `{"family_margin": -0.987698785092, "hint_id": "modal-synthesis-a5d39ab947233465", "predicted_family": "frame", "priority": 0.995045075793, "sample_id": "us-code-22-7602-56087c10d6c3e9c5", "target_family": "conditional_normative", "target_probability": 0.004954924207}`
- `program-fc45b4ceec109c01`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `0.989342`
  loss: `autoencoder_residual_cluster` = `0.913798275268`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-19-1508-90626a0f8c754dce, us-code-34-20921-9a0f066af01b89be, us-code-25-957-752853144a70e787, us-code-29-31-84bc08150f2562ea`
  evidence: `{"family_margin": -0.888979803204, "hint_id": "modal-synthesis-24ec24de0620929c", "predicted_family": "frame", "priority": 0.947129454024, "sample_id": "us-code-25-957-752853144a70e787", "target_family": "conditional_normative", "target_probability": 0.052870545976}`
  evidence: `{"family_margin": -0.952377179972, "hint_id": "modal-synthesis-3f9e3fa931c93e6b", "predicted_family": "frame", "priority": 0.978359276975, "sample_id": "us-code-34-20921-9a0f066af01b89be", "target_family": "deontic", "target_probability": 0.021640723025}`
  evidence: `{"family_margin": -0.377630258689, "hint_id": "modal-synthesis-fc36a23c7d1ec684", "predicted_family": "deontic", "priority": 0.981761298279, "sample_id": "us-code-19-1508-90626a0f8c754dce", "target_family": "dynamic", "target_probability": 0.018238701721}`
  evidence: `{"family_margin": -0.168037952136, "hint_id": "modal-synthesis-fef3ff4c4f612b56", "predicted_family": "temporal", "priority": 0.747943071795, "sample_id": "us-code-29-31-84bc08150f2562ea", "target_family": "deontic", "target_probability": 0.252056928205}`
- `program-0afc9c857e37dd48`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `0.98445`
  loss: `autoencoder_residual_cluster` = `0.880562395862`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-3942-60a29efa67206b9d, us-code-18-797-9f95397c66584e64, us-code-19-1436-03f836d62061219f, us-code-22-1644k-198b937dc7e81677`
  evidence: `{"family_margin": -0.997867939822, "hint_id": "modal-synthesis-0dc85464a3b39090", "predicted_family": "frame", "priority": 0.999325445827, "sample_id": "us-code-18-797-9f95397c66584e64", "target_family": "temporal", "target_probability": 0.000674554173}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-46eaa6812e3c9625", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-22-1644k-198b937dc7e81677", "target_family": "deontic", "target_probability": 0.467156858576}`
  evidence: `{"family_margin": -0.962915743756, "hint_id": "modal-synthesis-89692f68cd2842bd", "predicted_family": "frame", "priority": 0.990142812482, "sample_id": "us-code-19-1436-03f836d62061219f", "target_family": "deontic", "target_probability": 0.009857187518}`
  evidence: `{"family_margin": -0.999156828816, "hint_id": "modal-synthesis-d5fcc7f66872bbfd", "predicted_family": "frame", "priority": 0.999938183717, "sample_id": "us-code-22-3942-60a29efa67206b9d", "target_family": "temporal", "target_probability": 6.1816283e-05}`
- `program-881d3eeecd84d77d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `0.983279`
  loss: `autoencoder_residual_cluster` = `0.864541519257`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-43-485h-325b6dd405014d87, us-code-43-620m.-e9baf8df4beca760, us-code-20-4303-2cfa428f1663e8b5, us-code-49-31302.-a9accdbfcd1e11fa`
  evidence: `{"family_margin": -0.987496489013, "hint_id": "modal-synthesis-1c7fda66cfc6da8a", "predicted_family": "frame", "priority": 0.995947767003, "sample_id": "us-code-43-485h-325b6dd405014d87", "target_family": "temporal", "target_probability": 0.004052232997}`
  evidence: `{"family_margin": -0.396670740767, "hint_id": "modal-synthesis-4ccc2e886dfea7b3", "predicted_family": "alethic", "priority": 0.770698294338, "sample_id": "us-code-20-4303-2cfa428f1663e8b5", "target_family": "deontic", "target_probability": 0.229301705662}`
  evidence: `{"family_margin": -0.352426852485, "hint_id": "modal-synthesis-57864b05def0d3a8", "predicted_family": "frame", "priority": 0.702468239539, "sample_id": "us-code-49-31302.-a9accdbfcd1e11fa", "target_family": "deontic", "target_probability": 0.297531760461}`
  evidence: `{"family_margin": -0.974579480022, "hint_id": "modal-synthesis-b8b77c59b93d028b", "predicted_family": "frame", "priority": 0.989051776149, "sample_id": "us-code-43-620m.-e9baf8df4beca760", "target_family": "deontic", "target_probability": 0.010948223851}`
- `program-155cbe4143089d99`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6ef7c7c03fcf6ed2` score `0.981861`
  loss: `autoencoder_residual_cluster` = `0.779849168647`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-3041-c49da1d75259d673, us-code-31-6904-714f9a12df496721, us-code-15-52-8e1157bd728bbdff, us-code-14-2531-98785d94b487049a`
  evidence: `{"family_margin": 0.007279991044, "hint_id": "modal-synthesis-08f22d73499cf2b2", "predicted_family": "deontic", "priority": 0.605209763238, "sample_id": "us-code-15-52-8e1157bd728bbdff", "target_family": "deontic", "target_probability": 0.394790236762}`
  evidence: `{"family_margin": -0.959785107952, "hint_id": "modal-synthesis-704a311acdacdc0c", "predicted_family": "frame", "priority": 0.987502145054, "sample_id": "us-code-31-6904-714f9a12df496721", "target_family": "deontic", "target_probability": 0.012497854946}`
  evidence: `{"family_margin": -0.912069343873, "hint_id": "modal-synthesis-b05bfc28a6916974", "predicted_family": "deontic", "priority": 0.997600654363, "sample_id": "us-code-12-3041-c49da1d75259d673", "target_family": "temporal", "target_probability": 0.002399345637}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-d35ba68a20af608e", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-14-2531-98785d94b487049a", "target_family": "frame", "target_probability": 0.470915888067}`
