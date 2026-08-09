# News Intelligence Platform — Cleanup Candidates Audit

**Project Root:** `d:\project\news-intelligence-platform\project`  
**Date:** August 9, 2026  

---

## Verified Obsolete & Legacy Candidates

The following files were audited for dependency references across the codebase:

| File Path | Description | Dependency Analysis | Status / Recommendation |
| :--- | :--- | :--- | :--- |
| `archive/old_crawlers/*.py` | Legacy crawler experiments. | No active imports in current pipeline (`ingestion_service.py` or `streaming/`). | ⚠️ Archive Candidate (Preserve in `archive/`) |
| `historical_crawlers/*_old.py` | Backup copy of historical content extractor. | Active extractor is `historical_crawlers/extractor.py`. | ⚠️ Safe to prune after final acceptance. |
| `backend.zip` | Legacy zip archive of backend code. | Non-code archive file. | ⚠️ Safe to remove. |
| `requirements_old.txt` | Outdated requirement pins. | Active files are `requirements.txt` and `requirements_current.txt`. | ⚠️ Safe to remove. |

---

## Safety Directive
No active production files or tests have been deleted. All active scripts reference centralized modules in `config.py`, `qc/`, `api/`, `nlp/`, `streaming/`, and `historical/`.
