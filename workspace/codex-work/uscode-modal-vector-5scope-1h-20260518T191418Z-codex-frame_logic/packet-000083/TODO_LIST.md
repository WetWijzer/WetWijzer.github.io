# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-d3a859419bc0eff2`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-d3a859419bc0eff2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.322624772521`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-38-7310A-219731bd25fca43f, us-code-26-646-0cfbbfe0c86b90ae, us-code-22-2779a-2f9baaa9ac52eacf, us-code-54-101511.-54b6ccb5549961cf`
  evidence: `{"frame_features": ["flogic:citation_title_number_parity:even", "flogic:source_id_title_number_parity:even", "slot:citation_title_number_parity:even", "slot:source_id_title_number_parity:even", "flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0"], "hint_id": "modal-synthesis-6ead4b483ba4ee3a", "priority": 0.323023176344, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf"}`
  evidence: `{"frame_features": ["flogic:exception_alnum_segment_kind_positioned:5:alpha", "flogic:exception_scope_alnum_segment_kind_positioned:4:alpha", "flogic:predicate_alnum_segment:c", "flogic:predicate_alnum_segment:respect", "flogic:predicate_token:c", "flogic:predicate_token:respect"], "hint_id": "modal-synthesis-7759447d0528ea27", "priority": 0.41847466304, "sample_id": "us-code-38-7310A-219731bd25fca43f"}`
  evidence: `{"frame_features": ["flogic:citation_title_section_primary_number_span_parity:even", "flogic:citation_title_section_terminal_number_span_parity:even", "flogic:interpreted_in_frame:administrative_notice_hearing", "flogic:interpreted_in_frame_term:administrative", "flogic:interpreted_in_frame_term:administrative_notice_hearing", "flogic:interpreted_in_frame_term:agency", "flogic:interpreted_in_frame_term:appeal", "flogic:interpreted_in_frame_term:deadline"], "hint_id": "modal-synthesis-9c5501bd71d9a945", "priority": 0.356852997198, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae"}`
  evidence: `{"hint_id": "modal-synthesis-9d202dda7a61c9fc", "priority": 0.192148253501, "sample_id": "us-code-54-101511.-54b6ccb5549961cf"}`
