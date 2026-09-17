# shadcn/ui Component Mapping & Django Implementation Strategy

**Phase:** D1 — Design Foundation  
**Reference Design System:** `shadcn/ui` (Radix UI / Tailwind primitives)  
**Target Environment:** Django Server-Rendered Architecture (`dashboard/`)  
**Date:** 2026-09-04  

---

## 1. Architectural Strategy: Translation, Not Migration

`shadcn/ui` is an open-source collection of reusable components built on Radix UI and Tailwind CSS. Because our application architecture is a robust **Django 5.2 server-rendered application**, migrating to React solely to adopt React-native component packages would introduce immense build overhead, duplicate state management, and break existing Python-native ML integration.

Instead, we translate shadcn's **visual tokens, DOM hierarchy, and interaction semantics** into clean, semantic Django templates supported by modern CSS custom properties and lightweight accessible JavaScript primitives (e.g., native HTML5 `<dialog>`, ARIA attributes, and optional Alpine.js).

---

## 2. Comprehensive Component Mapping Table

| Interface Element | shadcn Reference Component | Rationale & Design Goal | Django Implementation Strategy |
| :--- | :--- | :--- | :--- |
| **Application Sidebar** | `Sidebar` (`components/ui/sidebar.tsx`) | Collapsible left navigation providing persistent spatial orientation across 5 core views. | Server-rendered `<aside class="ui-sidebar">` using Django's `request.resolver_match.url_name` for active route indicators. Built with CSS grid/flex and CSS variables for width and collapsed states. |
| **Header / Topbar** | `Header` / `Breadcrumb` | Provides breadcrumb context, current page title, system health status, and theme toggle. | Server-rendered `<header class="ui-topbar">` with `{% block breadcrumb %}`, crisp 1px bottom border, and SVG icons. |
| **Section & Input Cards** | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent` | Encapsulates semantic groupings (e.g., Demographics, Anthropometrics) with clear visual boundaries. | Standardized semantic HTML: `<div class="ui-card"><div class="ui-card-header"><h3 class="ui-card-title">...</h3></div><div class="ui-card-content">...</div></div>` styled via `.ui-card` CSS tokens. |
| **Form Inputs (Text, Number)** | `Input` (`components/ui/input.tsx`) | 40px height, subtle border, visible focus ring (`ring-2 ring-primary`), accessible placeholder. | Django form widgets rendered as `<input class="ui-input" type="number" step="0.1" ...>`. Floating or inline unit badges (`kg/m²`, `cm`, `min/day`) embedded via input group wrappers. |
| **Select Dropdowns** | `Select` (`components/ui/select.tsx`) | Clean select trigger with chevron indicator and restrained options list. | Native HTML `<select class="ui-select">` styled with custom SVG chevron background, ensuring full accessibility and native mobile keyboard compatibility. |
| **Action Buttons** | `Button` (`components/ui/button.tsx`) | Distinct visual hierarchy (`default`, `secondary`, `outline`, `destructive`, `ghost`). | Button utility classes: `.ui-btn .ui-btn-primary` (solid primary for submit), `.ui-btn .ui-btn-outline` (subtle border for reset/clear), `.ui-btn .ui-btn-destructive` (for overrides/deletions). |
| **Status Indicators** | `Badge` (`components/ui/badge.tsx`) | Compact pill element communicating discrete state without visual aggression. | `<span class="ui-badge ui-badge-amber">Elevated Signal</span>` and `<span class="ui-badge ui-badge-slate">Non-Elevated</span>`. Uses muted background tints with high-contrast text. |
| **Screening Result Display** | `Card` + `Badge` + `Alert` | Central decision-support surface displaying signal, screening probability, and recommendation. | Dedicated result card with clear typographic hierarchy, semantic status badge, and immediate link to explanation. |
| **Probability Presentation** | `Progress` / `Meter` | Shows model probability relative to the 0.1389 threshold without implying 100% diagnostic certainty. | Semantic `<div class="ui-meter" role="meter" aria-valuenow="...">` displaying numeric percentage (`24.7%`) and a restrained horizontal bar with a distinct vertical marker at the `13.9%` threshold. |
| **XAI Factor Decomposition** | `Accordion` / `Collapsible` | Displays positive and negative term contributions from the GAM model, with progressive disclosure for details. | Pure HTML `<details class="ui-accordion">` and `<summary>` or lightweight JS toggle. Visual bars represent log-odds spline term magnitudes ($f_i(x_i)$). |
| **Human Review Actions** | `Card` + `ButtonGroup` | Explicit choice surface for accepting or overriding the AI screening referral. | Review card with two prominent, mutually exclusive action buttons: `[ Accept Recommendation ]` (primary outline) and `[ Override Recommendation ]` (amber/secondary). |
| **Human Override Modal** | `AlertDialog` (`components/ui/alert-dialog.tsx`) | High-friction confirmation modal requiring explicit clinical rationale before finalizing an override. | Accessible native HTML5 `<dialog class="ui-dialog" id="overrideModal">` with `.showModal()`, backdrop blur, trap focus, explicit form inputs for reason dropdown and clinical note, and `[Confirm Override]` / `[Cancel]` buttons. |
| **Stage-2 Lab Intake** | `Card` + `Input` + `Badge` | Interface for entering confirmatory venous HbA1c laboratory percentage. | Dedicated card with number input (`step="0.1"`), reference range indicator (Normal $<5.7\%$, Prediabetes $5.7\%-6.4\%$, Diabetes $\ge 6.5\%$), and disclaimer. |
| **Review Queue & History** | `Table`, `TableHeader`, `TableRow`, `TableCell` | Clean, high-density tabular view with sorting, filtering, and row click targets. | Server-rendered `<table class="ui-table">` with striped hover states, status badges, and clickable row targets navigating to detailed case audits. |
| **Pagination** | `Pagination` (`components/ui/pagination.tsx`) | Restrained pagination controls (`Previous`, page numbers, `Next`). | Django `Paginator` rendered using standard `.ui-pagination` link buttons, preserving active filter query parameters. |
| **Medical Disclaimers** | `Alert` (`components/ui/alert.tsx`) | Non-alarmist callout cards for legal and methodological guardrails. | `<div class="ui-alert ui-alert-info"><svg class="ui-alert-icon">...</svg><div class="ui-alert-content"><p class="ui-alert-title">Screening Disclaimer</p><p class="ui-alert-body">...</p></div></div>`. |
| **Clinical Term Definitions** | `Tooltip` (`components/ui/tooltip.tsx`) | Contextual definition popups for technical predictors (e.g., sedentary minutes). | Accessible CSS tooltips using `data-tooltip="..."` and `aria-label`, triggering on hover and keyboard focus. |

---

## 3. Implementation Blueprint for Key Components

### 3.1 Custom Card Component Pattern
```html
<div class="ui-card">
  <div class="ui-card-header">
    <div class="ui-card-header-icon">
      <!-- Accessible SVG icon -->
    </div>
    <div>
      <h3 class="ui-card-title">Demographic Information</h3>
      <p class="ui-card-description">Core biological attributes for baseline risk calculation.</p>
    </div>
  </div>
  <div class="ui-card-content">
    <!-- Form controls -->
  </div>
  <div class="ui-card-footer">
    <!-- Contextual actions or hints -->
  </div>
</div>
```

### 3.2 Accessible Override Dialog Pattern (`HTML5 <dialog>`)
```html
<dialog id="override-dialog" class="ui-dialog" aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <div class="ui-dialog-content">
    <div class="ui-dialog-header">
      <h2 id="dialog-title" class="ui-dialog-title">Confirm Clinical Override</h2>
      <p id="dialog-desc" class="ui-dialog-description">
        You are modifying the system's referral recommendation. Please document your clinical rationale.
      </p>
    </div>
    
    <form method="POST" action="{% url 'predictor:override' %}">
      {% csrf_token %}
      <input type="hidden" name="screening_id" value="{{ screening.id }}">
      
      <!-- Comparison Panel -->
      <div class="ui-comparison-grid">
        <div class="ui-comparison-col">
          <span class="ui-text-muted">System Recommendation</span>
          <span class="ui-badge ui-badge-amber">Refer for Stage-2 HbA1c</span>
        </div>
        <div class="ui-comparison-col">
          <span class="ui-text-muted">Human Clinical Decision</span>
          <span class="ui-badge ui-badge-slate">Do Not Refer At This Time</span>
        </div>
      </div>

      <!-- Structured Reason Dropdown -->
      <div class="ui-form-group">
        <label for="override_reason" class="ui-label">Clinical Reason (Required)</label>
        <select id="override_reason" name="override_reason" class="ui-select" required>
          <option value="" disabled selected>Select primary clinical justification...</option>
          <option value="recent_normal_lab">Recent HbA1c normal within past 30 days</option>
          <option value="confounding_medication">Confounding medication affecting weight/glucose</option>
          <option value="frailty_palliative">Severe frailty / limited clinical utility of screening</option>
          <option value="patient_refusal">Patient declines laboratory referral after counseling</option>
          <option value="other">Other clinical justification (specify below)</option>
        </select>
      </div>

      <!-- Free Text Clinical Note -->
      <div class="ui-form-group">
        <label for="clinical_note" class="ui-label">Clinical Note</label>
        <textarea id="clinical_note" name="clinical_note" class="ui-textarea" rows="3" placeholder="Provide additional clinical context..." required></textarea>
      </div>

      <!-- Modal Footer -->
      <div class="ui-dialog-footer">
        <button type="button" class="ui-btn ui-btn-outline" onclick="document.getElementById('override-dialog').close()">Cancel</button>
        <button type="submit" class="ui-btn ui-btn-primary">Confirm & Log Override</button>
      </div>
    </form>
  </div>
</dialog>
```

---

## 4. Architectural Advantages of this Mapping

1. **Zero Node.js Dependency in Production:** All styles are compiled into a single clean CSS file (`style.css`), served natively via Django's `staticfiles`.
2. **Native Accessibility:** Native HTML5 elements (`<dialog>`, `<select>`, `<details>`) provide built-in keyboard trapping, screen reader announcing, and focus management without external bundle bloat.
3. **100% Visual Fidelity to shadcn:** By adopting the exact CSS custom properties (HSL-based tokens), spacing scale (4px grid), and typographic hierarchy, the interface achieves the modern, restrained aesthetic of shadcn/ui.
