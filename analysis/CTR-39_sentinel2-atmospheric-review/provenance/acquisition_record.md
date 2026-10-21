# Acquisition record — 20 October 2026

New DOI records were obtained from api.crossref.org/works/<DOI>. HTTP 429 for Daggers2020, Jacobs2021, Henriques2022 and Doxani2023 was resolved with doi.org content negotiation (Accept: application/vnd.citationstyles.csl+json). Titles and authors were checked against first pages; original metadata responses are in outputs/intertidal_metadata/ and normalized records in outputs/source_records.json.

PDF URLs and SHA-256 values are recorded per source in outputs/source_records.json. scripts/restore_pdfs.py reconstructs the public library, refusing changed checksums or overwrites. Public MDPI PDF assets were used when browser HTML returned errors. Zoffoli was acquired through Universidad de Cádiz, Zarzuelo through Universidad de Granada. Thuy's legacy Kyoto link returned HTML; the current public DSpace bitstream content endpoint supplied the article. The PDF's first page verifies the title, authors, year, DOI and CC BY licence.

All nine added articles were read at the passages listed in outputs/intertidal_notes.json; downloaded/extracted full texts remain local and ignored by Git. No publication full text is uploaded in the deliverable source bundle. The official SentiWiki HTML is recorded separately as technical documentation, not a PDF or research article.
