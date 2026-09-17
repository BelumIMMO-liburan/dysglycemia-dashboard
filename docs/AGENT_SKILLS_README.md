# Agent Skills & Customization Reference

**Project:** Dysglycemia Screening Dashboard  
**Workspace:** `C:\Users\Felix\Documents\Skripsi`  
**Setup Phase:** D1.5  
**Date:** 2026-09-04  

---

## 1. What Are Project Skills?

Project skills are structured instruction files located in `.agents/skills/<name>/SKILL.md`
at the workspace root. They encode domain-specific knowledge, constraints, and
workflows that guide the AI agent during implementation.

**Key characteristics:**
- Skills are loaded **on-demand** (progressive disclosure) — only their names
  and descriptions appear in the agent's context by default.
- The full SKILL.md content is read when the agent determines the skill is
  relevant to the current task, or when explicitly referenced.
- Workspace skills have **higher precedence** than built-in skills.

---

## 2. Installed Project Skills

### Skill: `research-governance` (HIGHEST PRECEDENCE)

**Path:** [`.agents/skills/research-governance/SKILL.md`](file:///c:/Users/Felix/Documents/Skripsi/.agents/skills/research-governance/SKILL.md)

**Purpose:** Prevents dashboard implementation from violating the completed
thesis methodology. This is the single most important skill in the project.

**When it activates:**
- Writing or modifying model loading / inference code
- Applying the classification threshold
- Writing clinical language in templates
- Implementing human override logic
- Computing analytics metrics
- Any decision about which predictors to include/exclude

**What it encodes:**
- Frozen GAM model specification (n_splines=10, λ=10.0)
- Exactly 7 non-laboratory predictors (no HbA1c, no glucose)
- Immutable threshold: 0.1389
- Held-out test performance (read-only reference)
- Required vs prohibited clinical language
- Human override semantic rules
- Analytics denominator governance

---

### Skill: `dashboard-design`

**Path:** [`.agents/skills/dashboard-design/SKILL.md`](file:///c:/Users/Felix/Documents/Skripsi/.agents/skills/dashboard-design/SKILL.md)

**Purpose:** Guides all dashboard UI/UX implementation using the approved
Evidence-First Guided Review philosophy and shadcn/ui visual reference.

**When it activates:**
- Building HTML templates
- Writing CSS styles and design tokens
- Designing page layouts and navigation
- Choosing component patterns
- Making interaction design decisions
- Creating new views or modifying existing ones

**What it encodes:**
- Evidence-First Guided Review interaction model
- 10 core design principles
- shadcn/ui visual translation strategy
- Information architecture and route mapping
- Prohibited UI patterns (model selectors, threshold sliders, etc.)
- Component reference mapping (shadcn → Django)
- Design token direction (Clinical Neutral)

---

### Skill: `frontend-quality`

**Path:** [`.agents/skills/frontend-quality/SKILL.md`](file:///c:/Users/Felix/Documents/Skripsi/.agents/skills/frontend-quality/SKILL.md)

**Purpose:** Enforces frontend implementation quality standards including
accessibility (WCAG 2.1 AA), responsive design, code hygiene, and visual QA.

**When it activates:**
- Writing CSS or modifying styles
- Creating form elements or interactive controls
- Building data tables or navigation
- Reviewing frontend output for quality
- Testing responsive behavior
- Verifying accessibility compliance

**What it encodes:**
- WCAG 2.1 AA mandatory requirements
- Responsive breakpoints and behavior rules
- Template hygiene (partials, no duplication, no dead code)
- JavaScript standards (no unnecessary frameworks)
- CSS standards (custom properties, HSL, no !important)
- Visual QA checklist
- Prohibition on fake placeholder metrics

---

## 3. MCP vs Skill — Understanding the Distinction

| Aspect | MCP Server | Project Skill |
|:---|:---|:---|
| **What it is** | External tool integration (live API/service) | Structured instruction file (static markdown) |
| **How it works** | Connects to running processes/APIs providing tools | Read into agent context as guidance text |
| **Configuration** | `mcp_config.json` (JSON with server commands/URLs) | `.agents/skills/<name>/SKILL.md` (Markdown with YAML frontmatter) |
| **Examples** | Context7 (docs lookup), Chrome DevTools (browser), GitHub MCP (repos) | `research-governance`, `dashboard-design`, `frontend-quality` |
| **Can replace the other?** | No — MCPs provide runtime tools; skills provide knowledge | No — skills provide domain rules; MCPs provide live capabilities |

**Critical rule:** Do NOT attempt to recreate MCP functionality as a SKILL.md
file. MCPs run external processes; skills encode static domain knowledge.

---

## 4. Skill Precedence Rules

When multiple skills or guidelines conflict, the following precedence order
governs resolution:

| Priority | Source | Authority |
|:---|:---|:---|
| **1 (Highest)** | `research-governance` skill | Frozen thesis methodology — NEVER overridable |
| **2** | `design/d1/DASHBOARD_DESIGN_SPEC_V1.md` | Approved D1 master specification |
| **3** | `dashboard-design` skill | UI/UX implementation guidance |
| **4** | `frontend-quality` skill | Accessibility, responsive, and QA standards |
| **5** | Generic external skills or web guidelines | General best practices |

**Iron Rule:** No generic skill, external template, aesthetic preference, or
convenience shortcut may override research governance. If a design decision
conflicts with the frozen thesis methodology, the research governance skill wins.

---

## 5. How to Verify Skill Discovery

### Method 1: Check Agent Skill Listing

Ask the agent: *"What skills are available?"*

The agent should list all three project skills in addition to built-in skills:
- `research-governance`
- `dashboard-design`
- `frontend-quality`

### Method 2: Verify File Existence

```powershell
Get-ChildItem -Path '.agents\skills' -Recurse -Filter 'SKILL.md'
```

Expected output:
```
.agents\skills\dashboard-design\SKILL.md
.agents\skills\frontend-quality\SKILL.md
.agents\skills\research-governance\SKILL.md
```

### Method 3: Test Skill Activation

Ask the agent to perform a task that should trigger a skill. For example:
- Ask about changing the threshold → `research-governance` should activate and refuse.
- Ask about adding a model selector → `dashboard-design` should activate and refuse.
- Ask about using color-only status → `frontend-quality` should activate and correct.

### Discovery Timing

- **New conversations:** Skills are discovered automatically at conversation start.
- **Current conversation:** If skills were created mid-conversation, the agent
  may need to explicitly read the SKILL.md files using `view_file` to activate
  them. Full automatic discovery occurs on the next conversation or agent restart.

---

## 6. Maintaining Skills

### Adding a New Skill

1. Create directory: `.agents/skills/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body.
3. The agent discovers it automatically on next conversation start.

### Modifying a Skill

Edit the `SKILL.md` file directly. Changes take effect when the agent next
reads the file.

### Removing a Skill

Delete the skill directory. The agent will no longer discover it.

### Adding MCP Servers

Edit `C:\Users\Felix\.gemini\config\mcp_config.json` to add new MCP server
configurations. Restart the Antigravity IDE for changes to take effect.
