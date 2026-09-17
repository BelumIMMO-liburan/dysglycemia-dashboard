# Phase D2.3 Security Audit: Deserialization Integrity & Surface Hardening

**Phase:** D2.3  
**Status:** Audited & Verified  
**Date:** September 2026  
**Governing Skill:** `research-governance`  

---

## 1. Audit Scope & Security Objectives

Machine learning models stored as serialized Python `pickle` files pose inherent security challenges, primarily related to arbitrary code execution during deserialization. Furthermore, web intake surfaces are susceptible to Cross-Site Request Forgery (CSRF), injection attacks, and denial of service via malformed payload submissions.

This security audit reviews the safeguards implemented in Phase D2.3 to ensure robust system protection.

---

## 2. Safe Deserialization Architecture

### Threat Model
If an untrusted actor modifies or substitutes `gam_final.pkl` or `preprocessor.pkl`, invoking standard `pickle.load()` could execute arbitrary operating system commands.

### Mitigations Implemented:
1. **Cryptographic SHA-256 Pre-Validation:**
   Prior to opening any pickle file for deserialization, the file's SHA-256 checksum is calculated in binary chunks (`64KB` buffers) and strictly matched against hardcoded, immutable constants:
   - `GAM_SHA256`: `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d`
   - `PREPROCESSOR_SHA256`: `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d`
   If even a single bit differs, deserialization is aborted immediately.

2. **Scoped Namespace Unpickling (`SafePreprocessorUnpickler`):**
   The preprocessor artifact was serialized in Phase 5 under a script executed as `__main__`. Rather than allowing arbitrary module resolution, `SafePreprocessorUnpickler` overrides `find_class()`:
   ```python
   class SafePreprocessorUnpickler(pickle.Unpickler):
       def find_class(self, module: str, name: str):
           if name == "FrozenPreprocessor":
               return FrozenPreprocessor
           return super().find_class(module, name)
   ```
   This resolves `__main__.FrozenPreprocessor` strictly to the local, inspected class definition and prevents arbitrary code execution.

3. **Read-Only Model Storage:**
   The model files reside outside the web server's document root in `nhanes_feasibility_2021_2023/models_phase5/`. The web server process requires only read permissions (`r--`).

---

## 3. Web Surface Security & CSRF Protection

1. **CSRF Enforcement:**
   All POST endpoints (`/screening/new/` and `/screening/run/`) enforce Django's CSRF token validation (`{% csrf_token %}`). Direct cross-origin POSTs are rejected with HTTP 403 Forbidden.

2. **HTTP Method Restrictions:**
   The `/screening/run/` endpoint rejects GET requests and automatically redirects the client to `/screening/new/`, preventing accidental execution via URL scraping or link prefetching.

3. **Strict Type Coercion & Range Clamping:**
   All input parameters are converted from strings to strict types (`int`, `float`) only after passing validation constraints. Floating point values are checked for `NaN` and `Inf` to prevent numeric overflow exploits.

---

## 4. Privacy & Data Minimization

1. **Zero Database Persistence:**
   In Phase D2.3, the inference service functions completely ephemerally. No patient names, medical record numbers, or inference outputs are stored in the database.
2. **Ephemeral Memory Lifecycle:**
   Input parameters and probabilities exist only within the request/response lifecycle.

---

## 5. Security Posture Summary

The Stage-1 frozen GAM inference adapter satisfies all security benchmarks for a clinical research prototype. Deserialization risks are fully mitigated by pre-computed cryptographic checksums and scoped unpickling.
