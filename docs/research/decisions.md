# Design Decisions - supOS Bedrock

**Track non-obvious choices. Enable reversibility.**

---

## D001: Master Container Pattern

**Date:** 2025-10-12 | **Status:** Active

**Choice:** Single orchestration container (Nextcloud AIO pattern) vs multi-container management.

**Why:**
- Simplifies deployment (one command)
- Centralized lifecycle management
- Web UI abstracts Docker complexity
- Proven pattern (Nextcloud AIO production use)

**Trade:** Master has elevated Docker socket access (security consideration).

**Reversibility:** High (can pivot to multi-container if needed).

---

## D002: Python + Docker SDK

**Date:** 2025-10-12 | **Status:** Active

**Choice:** Python orchestrator over Go/Bash/Node.js

**Why:**
- Docker SDK well-maintained
- Async support for health checks
- Rapid prototyping (70-hour constraint)
- Web framework integration

**Trade:** Slightly higher memory vs Go.

**Reversibility:** Medium (rewrite cost ~20 hours).

---

## D003: Flask for Web UI

**Date:** 2025-10-12 | **Status:** Active

**Choice:** Flask over FastAPI/Django

**Why:**
- Lightweight (~5MB container addition)
- Template engine built-in
- Sufficient for management UI
- Fast development

**Trade:** Less modern than FastAPI.

**Reversibility:** High (UI is separate layer).

---

## Template for New Decisions

```markdown
## DXXX: [Title]

**Date:** YYYY-MM-DD | **Status:** Active/Superseded

**Choice:** [What was chosen]

**Why:** [2-3 bullet reasoning]

**Trade:** [Main disadvantage]

**Reversibility:** High/Medium/Low ([how to undo])
```