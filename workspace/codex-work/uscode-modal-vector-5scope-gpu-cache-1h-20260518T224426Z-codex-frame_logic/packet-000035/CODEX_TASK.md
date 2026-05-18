# packet-000035

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000035/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000035/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-de7e6a6725a58f03` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-de7e6a6725a58f03` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:predicate_token_count:2", "slot:predicate_token_count:2"], "hint_id": "modal-synthesis-3e68f1a440673388", "priority": 0.298862484483, "sample_id": "us-code-43-1627.-86f764d2d884a21f"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:pub", "flogic:predicate_token:pub", "flogic:predicate_token_suffix:pub"], "hint_id": "modal-synthesis-5a3ea79a07995cbd", "priority": 0.510881643268, "sample_id": "us-code-22-4304-c522266be75990ce"}`
  evidence: `{"frame_features": ["flogic:modal_cue:authorized"], "hint_id": "modal-synthesis-7daecf757cb41ed0", "priority": 0.789258173907, "sample_id": "us-code-5-8133-e9163264dc0fc8b4"}`
  evidence: `{"frame_features": ["family:selected_frame:alethic"], "hint_id": "modal-synthesis-91d39e8618696560", "priority": 0.743987245892, "sample_id": "us-code-7-1963-566d388fcbdb6135"}`
- `program-f5593334c90a75a6` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-de7e6a6725a58f03` score `0.982949`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["family:selected_frame:alethic", "family:selected_frame:epistemic"], "hint_id": "modal-synthesis-2167bc88f498bd47", "priority": 0.383833869745, "sample_id": "us-code-33-3035-a7915fcc2f74a46f"}`
  evidence: `{"frame_features": ["flogic:predicate_token_count:2", "slot:predicate_token_count:2", "flogic:condition_alnum_segment:if"], "hint_id": "modal-synthesis-7dae59c75bd369db", "priority": 0.665257955061, "sample_id": "us-code-22-441-10b6a4089d8de64e"}`
  evidence: `{"frame_features": ["flogic:citation_section_alnum_segment_count:2", "flogic:citation_section_component_profile:single_alphanumeric"], "hint_id": "modal-synthesis-910fd94d55388ac6", "priority": 0.436916586463, "sample_id": "us-code-42-300bb-2b88b2e88e183d1f"}`
  evidence: `{"frame_features": ["flogic:predicate_token_count:2", "slot:predicate_token_count:2"], "hint_id": "modal-synthesis-c1e5ad06fe5a6f50", "priority": 0.38128411255, "sample_id": "us-code-26-114-ccb6bf617a6f040b"}`
- `program-087934c8b82a4b39` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-de7e6a6725a58f03` score `0.966827`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:modal_cue:required"], "hint_id": "modal-synthesis-18e349b677b3fac2", "priority": 0.318697776318, "sample_id": "us-code-20-1098cc-ec3688903d9caaf0"}`
  evidence: `{"hint_id": "modal-synthesis-4124a53652c3938d", "priority": 0.251648376054, "sample_id": "us-code-18-5041-b043586cd971c29a"}`
  evidence: `{"frame_features": ["family:frame:2", "flogic:modal_family_count:frame:2", "flogic:modal_family_count_frame:2"], "hint_id": "modal-synthesis-57f8be770b83264c", "priority": 0.407798880046, "sample_id": "us-code-7-511s-d96fcc7f71d0b18b"}`
  evidence: `{"frame_features": ["flogic:predicate_token_count:5", "slot:predicate_token_count:5", "flogic:predicate_alnum_segment_positioned:4:section"], "hint_id": "modal-synthesis-ed47a7ab84ddc4b3", "priority": 0.504500065231, "sample_id": "us-code-7-9056-0e619f90c16522bf"}`
- `program-239dd65d33d03329` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-de7e6a6725a58f03` score `0.960972`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:predicate_token_suffix:act", "slot:predicate_token_suffix:act"], "hint_id": "modal-synthesis-02e090f6940c735d", "priority": 0.60586249055, "sample_id": "us-code-25-500m-043f90b02f7839ad"}`
  evidence: `{"hint_id": "modal-synthesis-2911ca312709d53f", "priority": 0.402282899388, "sample_id": "us-code-15-1200-5601a302f976a9ea"}`
  evidence: `{"hint_id": "modal-synthesis-8c4843426d22f013", "priority": 0.213424379658, "sample_id": "us-code-10-14303-66f5bb7618836ade"}`
  evidence: `{"hint_id": "modal-synthesis-9eb23cd46c4f403c", "priority": 0.287433053626, "sample_id": "us-code-46-55335.-66c91ff89c8def29"}`
- `program-f16c1213fda48840` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-de7e6a6725a58f03` score `0.958018`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["family:selected_frame:conditional_normative", "flogic:modal_family:conditional_normative"], "hint_id": "modal-synthesis-2a64149ad38e8000", "priority": 0.602682315828, "sample_id": "us-code-15-171-15968f6d84c5fbe5"}`
  evidence: `{"frame_features": ["family:selected_frame:alethic", "flogic:citation_section_number_leading_digit:2", "flogic:citation_section_terminal_number_leading_digit:2", "flogic:citation_title_number_parity:odd", "flogic:condition_alnum_segment:any", "flogic:condition_alnum_segment:before", "flogic:condition_alnum_segment:for"], "hint_id": "modal-synthesis-2b7f5b2df3316d49", "priority": 0.345522639376, "sample_id": "us-code-51-20143.-781beb6660108834"}`
  evidence: `{"hint_id": "modal-synthesis-82a17a1570bf9551", "priority": 0.286008232296, "sample_id": "us-code-34-20126-b24c5e64ee5b952d"}`
  evidence: `{"frame_features": ["flogic:modal_cue:authorized", "flogic:predicate_alnum_segment_positioned:5:shall"], "hint_id": "modal-synthesis-95e678e00dc357ee", "priority": 0.505713327024, "sample_id": "us-code-22-2360-7fe8ccb179c7e3e4"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
