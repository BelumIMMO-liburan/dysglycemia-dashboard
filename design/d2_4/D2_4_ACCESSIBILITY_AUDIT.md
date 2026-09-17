# Phase D2.4 Accessibility Audit: WCAG 2.1 AA Compliance Verification

**Phase:** D2.4  
**Status:** Audited & Compliant  
**Date:** September 2026  
**Standards:** WCAG 2.1 Level AA, Evidence-First Clinical Ergonomics  

---

## 1. Audit Overview

The Stage-1 Screening Result view (`/screening/<uuid>/result/`) was evaluated for strict compliance with WCAG 2.1 AA accessibility guidelines. Clinical decision-support tools must be fully usable by individuals relying on screen readers, keyboard navigation, and high-contrast rendering.

---

## 2. Accessibility Checklist & Test Results

| WCAG 2.1 Criteria | Requirement | Implementation in Phase D2.4 | Status |
| :--- | :--- | :--- | :--- |
| **1.3.1 Info and Relationships** | Logical heading hierarchy and semantic grouping. | Single `<h1>` for page title, `<h2>` for primary result card, `<h3>` for interpretation section. All data points enclosed in semantic review grids. | **PASSED** |
| **1.4.1 Use of Color** | Color is never used as the sole conveyor of information. | All statuses couple **Icon + Text Label + Color**: e.g., amber badge includes warning SVG, text *"Elevated screening signal"*, and distinct background tone. | **PASSED** |
| **1.4.3 Contrast (Minimum)** | Text contrast $\ge 4.5:1$ against backgrounds; large text $\ge 3:1$. | Foreground text (`#0f172a`) on card (`#ffffff`) yields $>15:1$. Amber warning text on badge yields $>5.2:1$. Muted labels (`#64748b`) yield $>4.6:1$. | **PASSED** |
| **1.4.11 Non-text Contrast** | UI components and graphics contrast $\ge 3:1$. | SVG icons and card borders satisfy minimum $3:1$ contrast against adjacent canvas surfaces. | **PASSED** |
| **2.1.1 Keyboard Navigation** | All interactive elements operable via keyboard. | All buttons (`[ Start New Screening ]`, `[ Return to Overview ]`) and `<details>` disclosures are fully reachable and toggleable via `Tab` and `Space/Enter`. | **PASSED** |
| **2.4.4 Link / Button Purpose** | Purpose of each interactive control clear from context. | Explicit button labels: `"Start New Screening"` and `"Return to Overview"`. No ambiguous "Click here" labels. | **PASSED** |
| **4.1.2 Name, Role, Value** | Standard accessible roles and values for assistive tech. | Status badges use accessible SVG attributes (`aria-hidden="true"` with accompanying text). Disclosures utilize native HTML5 `<details>` and `<summary>`. | **PASSED** |

---

## 3. Screen Reader UX & Non-Alarmist Phrasing

1. **No Auto-Announced Alarms:** The page load does not trigger jarring audio alerts or aggressive aria-live announcements.
2. **Clear Quantitative Context:** The probability callout is explicitly announced as *"Screening probability"* with tabular numerals, followed by the recommendation *"Referral for Stage-2 HbA1c assessment is recommended."*
3. **Disclosure Accessibility:** Native `<details>` elements allow screen reader users to skip or expand secondary technical provenance without cognitive overload.
