# Laporan Verifikasi Keterhubungan Data & Dry-Run Sistem (Data Linkage & Dry-Run Report)
## Verifikasi Keterhubungan Multi-Instrumen Non-Human Menggunakan Skenario Baku (DRYRUN001)

**Kode Dokumen:** `E2-DRYRUN-REPORT-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Status Sesi:** PENELITI SAJA — NON-HUMAN SYNTHETIC VERIFICATION  
**Tanggal Eksekusi:** 2026-09-05  
**Identifikator Uji Coba:** `DRYRUN001`  
**Lingkungan Basis Data:** `dashboard/db_dryrun.sqlite3` (Terisolasi dari `db_study.sqlite3`)  

---

### 1. Ringkasan Eksekutif Dry-Run
Sebelum instrumen diserahkan kepada subjek manusia dalam sesi pilot, verifikasi *dry-run* peneliti deterministik dilakukan untuk:
1. Menguji eksekusi simulasi Tugas 1–6 terhadap prototipe beku (*research-prototype-v1.0*).
2. Memverifikasi keluaran inferensi model, arah faktor XAI, dan kategorisasi HbA1c Tahap-2.
3. Memastikan mekanisme *session database isolation* bekerja sempurna tanpa mencemari `db_study.sqlite3`.
4. Menguji algoritma perhitungan skor psikometrik SUS (Sharfina & Santoso 2016) dan kuis pemahaman objektif.
5. Memverifikasi keterhubungan kode (*exact participant-code linkage*) pada 7 berkas ekspor data dan basis data SQLite.

**Hasil Keseluruhan:** ✅ **100% LULUS (ALL ASSERTIONS PASSED)**

---

### 2. Verifikasi Eksekusi Tugas Antarmuka (Tasks 1–6)

| ID Tugas | Kasus Uji | Tindakan Pengujian | Hasil Aktual Sistem | Nilai Acuan Protokol E1 | Status |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **TASK 1 & 2** | `CASE-ALPHA` | Inferensi 7 input canonical & ekstraksi grafik XAI | $p = 0.272969$ (27.30%)<br>Rekomendasi: `Refer`<br>Sinyal: `Elevated Screening Signal`<br>Faktor Pendorong Teratas: `Age` (+0.418) | $p = 0.272969$<br>Rekomendasi: `Refer`<br>Sinyal: `Elevated`<br>Top Positive: `Age (+0.418)` | **PASSED** |
| **TASK 3** | `CASE-ALPHA` | Peninjauan Manusia (*Accept Recommendation*) | `review_action = 'accepted'`<br>`final_referral_recommended = True`<br>`reviewer_code = 'DRYRUN001'` | `accepted`<br>`refer`<br>`DRYRUN001` | **PASSED** |
| **TASK 4** | `CASE-BETA` | Inferensi Kasus Beta & *Human Override* ke Refer | $p = 0.054663$ (5.47%)<br>Rekomendasi Awal: `No Referral`<br>Sinyal: `Lower Screening Signal`<br>Aksi Override: `overridden`<br>Keputusan Akhir: `Refer`<br>Alasan Terstruktur: `precautionary_referral`<br>Catatan: *"Individual reports unrecorded family history of early diabetes"* | $p = 0.054663$<br>Rekomendasi: `No Referral`<br>Sinyal: `Lower`<br>Override: `overridden`<br>Keputusan: `Refer`<br>Alasan & Catatan persis | **PASSED** |
| **TASK 5** | `CASE-ALPHA` | Pencatatan Laboratorium HbA1c 6.1% | `hba1c_percent = 6.10%`<br>`laboratory_range = 'prediabetes_range'`<br>`entry_method = 'manual'` | `6.10%`<br>`prediabetes_range` | **PASSED** |
| **TASK 6** | `CASE-BETA` | Audit Jejak Riwayat & Status Tahap-2 | Rekomendasi awal AI tersimpan utuh (`No Referral`)<br>Jejak override tercatat permanen<br>Status Tahap-2: `Pending` (None) | Rekomendasi awal abadi<br>Tahap-2 pending | **PASSED** |

---

### 3. Verifikasi Kardinalitas Relasional & Integritas Basis Data

Setelah simulasi alur kerja dua kasus selesai pada `db_dryrun.sqlite3`:

```
1 Peserta (DRYRUN001)
   ├── 2 ScreeningRecord (Alpha & Beta)
   ├── 2 ScreeningExplanation (Alpha & Beta)
   ├── 2 HumanReview (Alpha: accepted, Beta: overridden)
   └── 1 Stage2Assessment (Alpha saja; Beta tetap pending)
```

- `ScreeningRecord.objects.count()`: **2** (Sesuai)
- `ScreeningExplanation.objects.count()`: **2** (Sesuai)
- `HumanReview.objects.count()`: **2** (Sesuai)
- `Stage2Assessment.objects.count()`: **1** (Sesuai)
- `Stage2Assessment` untuk Case Beta: **None / False** (Terbukti tidak melangkah ke Tahap-2)
- Nilai Hash Kriptografis Database Arsip:  
  `db_dryrun.sqlite3` SHA-256: `f78d75257068327c10a4e99dde3eabfb89a09d6beaa1a9a3a2f26befe4b365fe`

---

### 4. Pembuktian Kebersihan Basis Data Studi Formal (`db_study.sqlite3`)
Pemeriksaan langsung pada berkas kerja `dashboard/db_study.sqlite3` membuktikan bahwa eksekusi *dry-run* sama sekali tidak mencemari lingkungan data studi:
- `predictor_screeningrecord`: **0 baris**
- `predictor_screeningexplanation`: **0 baris**
- `predictor_humanreview`: **0 baris**
- `predictor_stage2assessment`: **0 baris**
- **Status `db_study.sqlite3`:** 🟢 **100% PRISTINE ZERO-STATE TERVERIFIKASI**

---

### 5. Verifikasi Algoritma Penilaian Skor Kuesioner

#### 5.1 Algoritma Penilaian System Usability Scale (SUS)
Formula resmi:
$$\text{SUS} = 2.5 \times \left( \sum_{k \in \text{odd}} (R_k - 1) + \sum_{k \in \text{even}} (5 - R_k) \right)$$

Uji coba fixture deterministik:
1. **Fixture 1 (Seluruh Butir Bernilai 4):**
   - Kontribusi Ganjil: $4 - 1 = 3$ (5 butir = 15)
   - Kontribusi Genap: $5 - 4 = 1$ (5 butir = 5)
   - Skor Terhitung: $2.5 \times (15 + 5) = 50.0$ | **LULUS (Expected: 50.0)**
2. **Fixture 2 (Skor Sempurna / Ganjil=5, Genap=1):**
   - Kontribusi Ganjil: $5 - 1 = 4$ (5 butir = 20)
   - Kontribusi Genap: $5 - 1 = 4$ (5 butir = 20)
   - Skor Terhitung: $2.5 \times (20 + 20) = 100.0$ | **LULUS (Expected: 100.0)**
3. **Fixture 3 (Pola Realistis 4/2 Bergantian):**
   - Kontribusi Ganjil: $4 - 1 = 3$ (5 butir = 15)
   - Kontribusi Genap: $5 - 2 = 3$ (5 butir = 15)
   - Skor Terhitung: $2.5 \times (15 + 15) = 75.0$ | **LULUS (Expected: 75.0)**

#### 5.2 Algoritma Penilaian Kuis Pemahaman Objektif (8 Butir)
- Kunci jawaban acuan: `COMP_01`=B, `COMP_02`=B, `COMP_03`=A, `COMP_04`=C, `COMP_05`=B, `COMP_06`=B, `COMP_07`=C, `COMP_08`=B.
- Respon sintetis uji: 7 jawaban benar, 1 salah (`COMP_04`=A).
- Skor terhitung: **7 / 8** (0 bobot ganda, murni 0/1 per butir). | **LULUS**

---

### 6. Audit Keterhubungan Kode Peserta (*Data Linkage Check*)

Ekspor 7 artefak data dilakukan ke direktori `evaluation/e2/runtime/dryrun_output/`:
1. `participants.csv`: 1 baris, kode `DRYRUN001` (100% matched)
2. `task_results.csv`: 6 baris (Tugas 1 s.d. 6), seluruhnya terhubung ke `DRYRUN001` dan UUID kasus yang tepat
3. `comprehension_responses.csv`: 8 baris, seluruhnya terhubung ke `DRYRUN001`
4. `sus_responses.csv`: 10 baris, seluruhnya terhubung ke `DRYRUN001`
5. `perception_responses.csv`: 5 baris, seluruhnya terhubung ke `DRYRUN001`
6. `qualitative_feedback.csv`: 3 baris, seluruhnya terhubung ke `DRYRUN001`
7. `session_manifest.csv`: 1 baris, mencatat hash database dan tautan berkas untuk `DRYRUN001`
8. `HumanReview.reviewer_code` dalam basis data SQLite: Tepat 2 baris bernilai `DRYRUN001`.

**Statistik Integritas Linkage:**
- Jumlah berkas tidak tertaut (*unmatched files*): **0**
- Duplikasi kode partisipan (*duplicate identifiers*): **0**
- Kebocoran informasi identitas (*unintended PII*): **0**

---

### 7. Kesimpulan Kesiapan Operasional
Hasil verifikasi *dry-run* membuktikan bahwa arsitektur evaluasi *hybrid*, prosedur isolasi basis data per sesi, skema penautan kode peserta, serta instrumen kuesioner eksternal telah **100% kompatibel dan terverifikasi secara matematis dan teknis**. Seluruh komponen operasional siap digunakan untuk sesi pilot segera setelah otorisasi institusional diterbitkan.
