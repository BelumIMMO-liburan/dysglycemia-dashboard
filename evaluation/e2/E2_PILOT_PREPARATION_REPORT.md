# Laporan Kesiapan Paket Operasional Pilot (Phase E2 Preparation Report)
## Paket Instrumen Pilot, Penyiapan Pengumpulan Data Hybrid, Isolasi Sesi, & Verifikasi Dry-Run

**Kode Dokumen:** `E2-PILOT-PREPARATION-REPORT-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Target Perangkat Lunak:** `research-prototype-v1.0` (Status: Terkunci / Frozen)  
**Status Otorisasi Partisipan:** 🔴 **NOT YET AUTHORIZED BY THIS PHASE**  
**Tanggal Penerbitan:** 2026-09-05  

---

### 1. Ringkasan Eksekutif & Status Keseluruhan E2
Fase E2 telah menyelesaikan secara tuntas seluruh persiapan paket operasional yang dipersyaratkan untuk menyelenggarakan studi kelayakan (*feasibility pilot*, $N=3\text{--}5$) tanpa mengubah sebaris pun kode sumber aplikasi prototipe maupun artefak model machine learning beku (*research-prototype-v1.0*).

**Pencapaian Kunci Fase E2:**
1. **Arsitektur Pengumpulan Data Hybrid Terkunci:** Memisahkan lingkungan tugas antarmuka (Django Web Prototype) dari instrumen psikometrik kuesioner pasca-tugas (Platform Survei Digital Eksternal) dan lembar observasi moderator terstruktur.
2. **Paket Materi Peserta Siap Pakai:** 7 dokumen berbahasa Indonesia baku tersusun rapi di direktori `materials/participant/`, teruji 100% bebas dari kebocoran probabilitas model, bobot kontribusi GAM, dan kunci jawaban.
3. **Instrumen Moderator Terisolasi:** Kunci status keluaran sistem, rubrik observasi terstruktur, dan petunjuk teknis 13-langkah tersusun di direktori `materials/moderator/`.
4. **Cetak Biru Kuesioner Eksternal & Setelan Privasi:** Blueprint 5 seksi platform-agnostik memuat 8 butir kuis pemahaman objektif terkunci E1, 10 butir SUS adaptasi Sharfina & Santoso (2016), 5 butir kejelasan alur, serta panduan pencegahan pengumpulan email/akun otomatis.
5. **Isolasi Sesi Basis Data Terverifikasi:** Mekanisme basis data sesi terisolasi berbasis kloning template bersih (`db_session_template.sqlite3` $\to$ `db_study.sqlite3`) menjamin riwayat peserta sebelumnya tidak pernah terlihat oleh peserta berikutnya.
6. **Verifikasi Dry-Run Peneliti (DRYRUN001) Sukses 100%:** Eksekusi deterministik Tugas 1–6 membuktikan kardinalitas relasional, integritas hash SHA-256 arsip database, kompatibilitas formula skor SUS dan pemahaman, serta penautan kode peserta tanpa celah di seluruh artefak data.
7. **Gerbang Otorisasi Pra-Pilot Terkunci Rapat:** Dokumen gerbang menetapkan status formal **NOT AUTHORIZED FOR PARTICIPANT CONTACT** hingga persetujuan dosen pembimbing dan komite etik institusi diterbitkan secara definitif.

---

### 2. Arsitektur Evaluasi Hybrid & Batasan Bukti

```
+-----------------------------------------------------------------------------------+
|                           ARSITEKTUR EVALUASI HYBRID                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [DASHBOARD WEB LOKAL]       [KUESIONER DIGITAL EKSTERNAL]    [LEMBAR OBSERVASI]   |
|   research-prototype-v1.0     Google/MS Forms / Qualtrics      Moderator Sheet    |
|   (Tugas Interaksi 1 s.d 6)   (Post-Task Psychometrics)        (Assistance/Errors)|
|             │                               │                          │          |
|             ▼                               ▼                          ▼          |
|   db_study.sqlite3               survey_export.csv          moderator_log.csv     |
|   (HumanReview.reviewer_code)    (Participant Code)         (Participant Code)    |
|             │                               │                          │          |
|             └───────────────────────┬───────┴──────────────────────────┘          |
|                                     ▼                                             |
|                      [KUNCI PENAUT: PARTICIPANT CODE]                             |
|                        (PILOT001, PILOT002, P001, dst)                            |
+-----------------------------------------------------------------------------------+
```

**Justifikasi Metodologis:**
- Menjaga kebekuan mutlak rilis prototipe penelitian (*zero application changes*).
- Menghilangkan risiko regresi sistem atau dependensi model Django kuesioner ad-hoc.
- Memisahkan data bukti alur kerja skrining/peninjauan (*screening/review workflow data*) dari data pengukuran ergonomis dan pemahaman.

---

### 3. Skema Kode Peserta & Tata Kelola Privasi Dua Brankas

Sintaks kode terstandarisasi:
- **Sesi Pengujian Kelayakan (Pilot):** `PILOT001` s.d. `PILOT005`
- **Sesi Studi Formal Masa Depan:** `P001` s.d. `P030`
- **Sesi Dry-Run Teknis Peneliti:** `DRYRUN001`

**Semantik Kode Peserta (*Pseudonymous Research Identifier*):**
Kode Peserta berfungsi murni sebagai pengidentifikasi riset pseudonim (*pseudonymous research identifier*). Penggunaan kode ini memfasilitasi penautan relasional data multi-instrumen tanpa memuat data identitas personal langsung di dalam dataset analitis. Kode peserta **bukan** bukti anonimisasi ireversibel selama tautan pemetaan identitas-kode administratif masih tersimpan terpisah di Brankas A. Seluruh data penelitian yang bertaut kode ini diklasifikasikan secara presisi sebagai **data penelitian pseudonim**, bukan data yang sepenuhnya anonim.

**Pemisahan Data Dua Brankas (*Two-Vault Governance*):**
- **Brankas A (Administratif Terbatas / Administrative Restricted Vault):** Menyimpan lembar persetujuan (*informed consent*) bertanda tangan fisik/digital yang menghubungkan nama/identitas subjek dengan kode peserta. Disimpan di direktori/map fisik terkunci terpisah dengan akses sangat terbatas bagi pengelola administrasi etik. Berkas ini **eksklusif terisolasi dan tidak pernah disertakan dalam dataset analisis penelitian**.
- **Brankas B (Dataset Analisis Pseudonim / Terbatas):** Menyimpan seluruh basis data SQLite sesi, rekaman observasi moderator, dan respon kuesioner pasca-tugas. Hanya menggunakan kode peserta pseudonim, bebas dari data identitas personal langsung (tanpa nama, email, nomor induk mahasiswa, atau nomor telepon). Akses dibatasi ketat hanya untuk tim peneliti dan **tidak bersifat publik/terbuka secara bebas** (*restricted access, not public by default*).

**Pernyataan Tata Kelola PII Langsung (*Direct PII Governance Claim*):**
> Tidak ada PII langsung (*direct PII*) yang dikumpulkan dalam kuesioner analitis, rekaman alur kerja skrining/peninjauan antarmuka, dataset observasi moderator, atau ekspor analisis. Segala informasi identitas yang diperlukan untuk persetujuan (*informed consent*) / administrasi rekrutmen disimpan secara terpisah di bawah tata kelola administratif terbatas (Brankas A).

---

### 4. Inventaris Dokumen & Kesiapan Materi

#### 4.1 Materi Peserta (`evaluation/e2/materials/participant/`)
1. `E2_PARTICIPANT_INFORMATION_SHEET_ID.md`: Lembar informasi peserta berbahasa Indonesia, menegaskan batasan non-medis dan penggunaan kasus sintetis (bebas PII pra-sesi, tidak mengumpulkan PII).
2. `E2_CONSENT_FORM_DRAFT_ID.md`: Draf formulir persetujuan keikutsertaan sukarela (bebas PII pra-sesi pada dokumen blanko; mengumpulkan tanda tangan/persetujuan peserta saat diisi; disimpan di Brankas A Administratif Terbatas; tidak masuk ke dataset analisis).
3. `E2_PARTICIPANT_TASK_BOOKLET_ID.md`: Buku panduan pengerjaan Tugas 1 s.d. 6 dengan label antarmuka beku (bebas PII, tidak mengumpulkan PII).
4. `E2_CASE_CARD_ALPHA_ID.md`: Kartu stimulus Case Alpha (hanya 7 nilai canonical, tanpa probabilitas, tanpa PII).
5. `E2_CASE_CARD_BETA_ID.md`: Kartu stimulus Case Beta (hanya 7 nilai canonical, tanpa probabilitas, tanpa PII).
6. `E2_STAGE2_CASE_ALPHA_CARD_ID.md`: Kartu input HbA1c 6.1% (tanpa membocorkan label rentang, tanpa PII).
7. `E2_OVERRIDE_SCENARIO_BETA_ID.md`: Kartu skenario instruksi pengesampingan (*override*) Case Beta dengan alasan terstruktur dan catatan simulasi (tanpa PII).

#### 4.2 Materi Moderator (`evaluation/e2/materials/moderator/`)
1. `E2_MODERATOR_EXPECTED_STATE_KEY.md`: Kunci acuan operasional sistem, probabilitas persis ($0.272969$ dan $0.054663$), bobot kontribusi GAM, klasifikasi rentang lab, dan kunci kuis 8 butir (bebas PII).
2. `E2_MODERATOR_OBSERVATION_SHEET.md`: Lembar cetak observasi logging kinerja tugas berbeban rendah (hanya mencatat Kode Peserta, Brankas B).
3. `E2_PILOT_MODERATOR_RUNBOOK.md`: Petunjuk teknis terinci 13 langkah operasional pelaksanaan sesi (memuat instruksi penyimpanan Brankas A untuk lembar consent).

#### 4.3 Formulir Kuesioner Eksternal (`evaluation/e2/forms/`)
1. `E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md`: Blueprint 5 seksi platform-agnostik.
2. `E2_EXTERNAL_FORM_CONFIGURATION.md`: Panduan toggle privasi (mematikan kumpul email, mematikan login akun, mematikan nilai langsung).

#### 4.4 Template Basis Data Studi (`evaluation/e2/templates/`)
- `session_manifest.csv`
- `moderator_observation_template.csv`
- `pilot_incident_log.csv`
- `participants.csv`
- `task_results.csv`
- `comprehension_responses.csv`
- `sus_responses.csv`
- `perception_responses.csv`
- `qualitative_feedback.csv`

---

### 5. Hasil Eksekusi Dry-Run Deterministik (DRYRUN001)

Simulasi end-to-end peneliti berhasil membuktikan:
1. **Ketepatan Nilai Inferensi & Penjelasan:**
   - Case Alpha: Probabilitas $= 0.272969$, Rekomendasi $= \text{Refer}$, Sinyal $= \text{Elevated}$, Faktor Positif Teratas $= \text{Age } (+0.418)$.
   - Case Beta: Probabilitas $= 0.054663$, Rekomendasi $= \text{No Referral}$, Sinyal $= \text{Lower}$.
2. **Alur Peninjauan & Pengesampingan:**
   - Case Alpha: Berhasil diterima (*accepted*) dengan kode `DRYRUN001`.
   - Case Beta: Berhasil dikesampingkan (*overridden*) ke *Refer* dengan alasan terstruktur `precautionary_referral` dan catatan simulasi keluarga.
3. **Penilaian Tahap-2 & Integritas Kardinalitas:**
   - Case Alpha: Nilai HbA1c 6.10% berhasil diklasifikasikan ke `prediabetes_range`.
   - Case Beta: Tetap berstatus *Pending Stage-2 Assessment*.
   - Kardinalitas basis data sesi: Tepat 2 ScreeningRecords, 2 ScreeningExplanations, 2 HumanReviews, 1 Stage2Assessment.
4. **Isolasi Database & Hash Kriptografis:**
   - `db_dryrun.sqlite3` SHA-256: `f78d75257068327c10a4e99dde3eabfb89a09d6beaa1a9a3a2f26befe4b365fe`.
   - `db_study.sqlite3` diverifikasi tetap bersih 100% (0 baris di seluruh tabel).
5. **Kompatibilitas Penilaian Skor Kuesioner:**
   - Skor SUS teruji deterministik: Seluruh 4s $= 50.0$; Sempurna $= 100.0$; Realistis 4/2 bergantian $= 75.0$.
   - Kuis pemahaman teruji: 7 benar dari 8 butir $= 7/8$.
6. **Penautan Kode Peserta (Data Linkage Audit):**
   - 0 unmatched files, 0 duplicate identifiers, 0 unintended PII across all 7 CSV files and SQLite.

---

### 6. Status Gerbang Otorisasi & Bidang Tertunda (Pending Fields)

Dokumen gerbang `evaluation/e2/E2_PRE_PILOT_AUTHORIZATION_GATE.md` mengunci status:
🔴 **NOT AUTHORIZED FOR PARTICIPANT CONTACT**

**Bidang yang Menunggu Keputusan Pembimbing / Institusi:**
1. Persetujuan formal pembimbing terhadap paket instrumen E2.
2. Penetapan kebutuhan kaji etik fakultas (*Ethical Clearance vs Exemption*).
3. Pengisian definitif placeholder informasi kontak:
   - Nama & surel peneliti utama
   - Nama & surel dosen pembimbing
   - Nama institusi/program studi resmi
   - Nomor registrasi komite etik
   - Periode retensi arsip data
4. Penetapan platform survei resmi (Google Forms institusi / MS Forms).
5. Penetapan status wajib/opsional pertanyaan kualitatif terbuka (*Supervisor Decision Required*).

---

### 7. Verifikasi Kebekuan Prototipe & Test Suite

- **Kode Aplikasi Prototipe:** Tidak disentuh (0 berkas di `dashboard/predictor/` yang diubah).
- **Test Suite Otomatis:** **144 / 144 passing** (1.72s).
- **Integritas Berkas Kriptografis Riset:**
  - `gam_final.pkl`: `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` (VERIFIED)
  - `preprocessor_development.pkl`: `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` (VERIFIED)
  - `model_spec.json`: `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` (VERIFIED)
  - `final_test_predictions.csv`: `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` (VERIFIED)
