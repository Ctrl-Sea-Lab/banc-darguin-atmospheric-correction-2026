# Response to CTR-45 — limited intertidal corrections

**Take-home message:** Both requested corrections are applied. The recommendation remains Sen2Cor as a baseline for local testing, with qualified alternatives; no best processor for Banc d’Arguin is established.

**Meaningful results:** Zarzuelo’s intermediate-tide selection and separate low-tide habitat-zonation restriction are now recorded together. Doxani’s relevant section is corrected to §3.1.3, PDF p. 9.

**Issues and limitations:** Zarzuelo’s relationship between the tidal-selection statements remains unclear. No stage-specific tidal-selection rule is inferred. This response is an author correction, not independent acceptance.

**Implications and next steps:** Rebuild and audit the corrected report, then request a focused independent source/diff/reconstruction recheck on the exact submitted commit. PI approval and manuscript integration remain separate.

## Review addressed

- Independent review: CTR-45, document revision 95a57167-dbf5-43af-9f76-445f78cdeae2, 20 October 2026.
- Exact previously reviewed source: af8b45637a838d66ab6e53d08f154a93fc82817a.
- Verdict: Minor Revision; no critical or major concerns.

## M1 — Zarzuelo tidal-selection qualification

Re-inspected the existing primary PDF, pp. 7 and 12. Section 3.1 (p. 7) describes excluding extreme tides and retaining intermediate conditions. The Discussion (p. 12) restricts habitat zonation to low-tide images. Although the workflow distinguishes intertidal-extent detection from habitat classification, the relationship between the two selection statements remains unclear. The report now preserves that ambiguity instead of assigning intermediate tides to zonation. Low-tide selection for the present exposed-sediment question remains appropriate.

Updated the report’s first comparison table and accompanying narrative, authoritative outputs/intertidal_notes.json, and literature/search_log.md. Rebuilding generates the corresponding reference-index and evidence-matrix corrections.

## E1 — Doxani source locator

Re-inspected the existing primary PDF p. 9. The surface-reflectance exclusion and reference-method caveats are in §3.1.3. Corrected the authoritative notes from §3.2.1 and rebuilt the derived evidence and index. Scientific summary unchanged.

## Scope and verification

No new reference, processor ranking, numerical performance claim, source PDF or raw dataset is introduced. The preserved prior water review, final manuscript, shared bibliography, manuscript configuration and dependency lockfiles remain protected. Validation results are recorded in outputs/audit_results.json; the exact submission commit is supplied in the Paperclip handoff because a file cannot record its own final Git commit hash.

Author validation completed on 20 October 2026: library reconstruction and standalone render exited 0 without warnings; the audit passed with 14 resolved cited references, 27 library records, 24 identity/checksum-checked PDFs, two rendered comparison tables, seven unchanged protected files and 18 verified prior-snapshot entries. Review of the diff confirmed that recommendations, numerical-claim records, bibliography content, PDF files and reconstruction scripts were unchanged. These are author checks; independent recheck remains pending.
