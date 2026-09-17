# Manifes Paket Operasional Pilot (Pilot Package Manifest)
## Inventaris Lengkap Seluruh Berkas, Instrumen, dan Template Evaluasi E2

**Kode Dokumen:** `E2-PACKAGE-MANIFEST-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tanggal Penerbitan:** 2026-09-05  

---

### 1. Rekapitulasi Tata Kelola Berkas & Dimensi Privasi
Sesuai prinsip tata kelola riset (*Research Governance*), seluruh 33 artefak dalam paket E2 dipilah secara tegas berdasarkan audiens, tingkat kerahasiaan kunci jawaban, dan empat dimensi tata kelola privasi:
1. **Memuat PII Pra-Sesi (*Pre-existing PII in Blank Artifact*):** Apakah berkas acuan/draf kosong mengandung data identitas subjek? (Seluruh artefak kosong = `NO`).
2. **Mengumpulkan PII Saat Selesai (*Collects Direct PII When Completed*):** Apakah instrumen merekam identitas langsung/tanda tangan saat diisi oleh subjek?
   - Draf Lembar Persetujuan (`E2_CONSENT_FORM_DRAFT_ID.md`): `YES` (mengumpulkan tanda tangan/persetujuan peserta bertaut Kode Peserta untuk administrasi etik).
   - Seluruh instrumen lainnya (Materi Tugas, Kuesioner Eksternal, Template CSV, dsb.): `NO` (hanya menggunakan Kode Peserta pseudonim atau data teknis).
3. **Domain Penyimpanan (*Data/Storage Domain*):**
   - **Brankas A (Administratif Terbatas / Administrative Restricted Vault):** Berkas persetujuan bertanda tangan fisik/digital, terisolasi dengan akses terbatas.
   - **Brankas B (Dataset Analisis Pseudonim / Terbatas):** Basis data sesi, observasi, respon kuesioner, dan template CSV analitis (akses tim peneliti, tidak terbuka untuk umum).
   - **Materi Operasional / Publik Sesi:** Panduan, kartu stimulus kasus, dan spesifikasi instrumen.
4. **Termasuk dalam Dataset Analisis (*Included in Analytical Dataset*):**
   - Lembar persetujuan: `NO` (terisolasi penuh dari dataset analisis).
   - Template dan respon penelitian: `YES` (hanya dalam format pseudonim ber-Kode Peserta).

| Aturan Tata Kelola | Standar Kepatuhan Privasi & Kerahasiaan |
| :--- | :--- |
| **Materi Peserta (*Participant Materials*)** | Wajib: `Contains Answer Key = NO`, `Contains Pre-existing PII = NO`. Lembar persetujuan mencatat tanda tangan saat diisi dan disimpan di Brankas A (terisolasi dari analisis). Materi tugas lainnya `Collects PII = NO`. |
| **Materi Moderator (*Moderator Materials*)** | Boleh memuat kunci jawaban (`Contains Answer Key = YES`). Wajib: `Pre-existing PII = NO`, `Collects PII = NO` (hanya kode peserta). |
| **Kuesioner Eksternal (*External Survey Forms*)** | Wajib: `Contains Answer Key = NO`, `Pre-existing PII = NO`, `Collects PII = NO` (bebas dari pengumpulan akun/email; hanya kode peserta). |
| **Template Data (*Study Data CSV Templates*)** | Wajib: Struktur kolom kosong identik 100% dengan `E1_STUDY_DATA_SCHEMA.md`. Disimpan di Brankas B (Pseudonim/Terbatas). |

---

### 2. Tabel Inventaris Lengkap Berkas Paket E2

| No | Lokasi Relatif / Nama Berkas | Tujuan Berkas (*Purpose*) | Target Audiens (*Audience*) | Memuat Kunci? | PII Pra-Sesi? | Kumpul PII Selesai? | Domain Penyimpanan & Analisis |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **A** | **DOKUMEN OPERASIONAL & ARSITEKTUR UTAMA** | | | | | | |
| 1 | `evaluation/e2/E2_HYBRID_COLLECTION_ARCHITECTURE.md` | Arsitektur evaluasi hybrid (dashboard terpisah dari kuesioner) | Tim Peneliti | NO | NO | NO | Dokumen Tata Kelola |
| 2 | `evaluation/e2/E2_PARTICIPANT_CODE_SCHEME.md` | Tata kelola sintaks kode peserta (`PILOT001`, `P001`, `DRYRUN001`) | Tim Peneliti | NO | NO | NO | Dokumen Tata Kelola |
| 3 | `evaluation/e2/E2_SESSION_DATABASE_PROTOCOL.md` | Prosedur per-session database isolation (kloning & pengarsipan) | Tim Peneliti | NO | NO | NO | Dokumen Tata Kelola |
| 4 | `evaluation/e2/E2_SURVEY_PLATFORM_DECISION.md` | Analisis komparatif & panduan konfigurasi platform kuesioner | Peneliti / Supervisor | NO | NO | NO | Dokumen Tata Kelola |
| 5 | `evaluation/e2/E2_PRE_PILOT_AUTHORIZATION_GATE.md` | Gerbang kepatuhan otorisasi pra-pilot (status: NOT AUTHORIZED) | Peneliti / Komite Etik | NO | NO | NO | Dokumen Tata Kelola |
| 6 | `evaluation/e2/E2_PILOT_EXECUTION_CHECKLIST.md` | Daftar periksa kontrol kualitas sesi pilot (sebelum, saat, setelah) | Moderator | NO | NO | NO | Panduan Operasional |
| 7 | `evaluation/e2/E2_POST_PILOT_CHANGE_DECISION_TEMPLATE.md` | Kerangka klasifikasi keputusan perubahan pasca-pilot | Peneliti / Supervisor | NO | NO | NO | Dokumen Tata Kelola |
| 8 | `evaluation/e2/E2_DATA_LINKAGE_DRYRUN_REPORT.md` | Laporan hasil pengujian end-to-end dry-run (DRYRUN001) | Tim Peneliti | YES (Hasil Uji) | NO | NO | Laporan Verifikasi Teknis |
| 9 | `evaluation/e2/E2_PILOT_PREPARATION_REPORT.md` | Laporan komprehensif penutupan persiapan operasional Fase E2 | Peneliti / Supervisor | NO | NO | NO | Laporan Tata Kelola |
| 10 | `evaluation/e2/E2_PILOT_PACKAGE_MANIFEST.md` | Dokumen manifes inventaris seluruh berkas paket E2 ini | Seluruh Pihak | NO | NO | NO | Dokumen Manifes |
| **B** | **MATERI PESERTA (PARTICIPANT MATERIALS)** | | | | | | |
| 11 | `evaluation/e2/materials/participant/E2_PARTICIPANT_INFORMATION_SHEET_ID.md` | Lembar informasi peserta berbahasa Indonesia & batasan non-medis | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Dibagikan) |
| 12 | `evaluation/e2/materials/participant/E2_CONSENT_FORM_DRAFT_ID.md` | Draf lembar persetujuan keikutsertaan (*informed consent*) | Peserta Evaluasi | **NO** | **NO** | **YES (Tanda Tangan)** | **Brankas A (Administratif Terbatas)**; Tidak Masuk Dataset Analisis |
| 13 | `evaluation/e2/materials/participant/E2_PARTICIPANT_TASK_BOOKLET_ID.md` | Buku panduan instruksi Tugas 1–6 (tanpa bocoran kunci/probabilitas) | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Operasional) |
| 14 | `evaluation/e2/materials/participant/E2_CASE_CARD_ALPHA_ID.md` | Kartu stimulus Case Alpha (hanya memuat 7 nilai input canonical) | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Operasional) |
| 15 | `evaluation/e2/materials/participant/E2_CASE_CARD_BETA_ID.md` | Kartu stimulus Case Beta (hanya memuat 7 nilai input canonical) | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Operasional) |
| 16 | `evaluation/e2/materials/participant/E2_STAGE2_CASE_ALPHA_CARD_ID.md` | Kartu input lab HbA1c 6.1% untuk Case Alpha (tanpa label rentang) | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Operasional) |
| 17 | `evaluation/e2/materials/participant/E2_OVERRIDE_SCENARIO_BETA_ID.md` | Kartu skenario instruksi pengesampingan (*override*) Case Beta | Peserta Evaluasi | **NO** | **NO** | **NO** | Materi Peserta (Operasional) |
| **C** | **MATERI MODERATOR & PENELITI** | | | | | | |
| 18 | `evaluation/e2/materials/moderator/E2_MODERATOR_EXPECTED_STATE_KEY.md` | Kunci status acuan sistem, probabilitas, bobot XAI, & kunci kuis | Moderator / Peneliti | **YES** | **NO** | **NO** | Materi Moderator (Terbatas) |
| 19 | `evaluation/e2/materials/moderator/E2_MODERATOR_OBSERVATION_SHEET.md` | Lembar cetak observasi logging kinerja peserta Tugas 1–6 | Moderator | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 20 | `evaluation/e2/materials/moderator/E2_PILOT_MODERATOR_RUNBOOK.md` | Petunjuk teknis 13 langkah operasional pelaksanaan sesi | Moderator | NO | NO | NO | Panduan Operasional |
| **D** | **FORMULIR KUESIONER DIGITAL EKSTERNAL** | | | | | | |
| 21 | `evaluation/e2/forms/E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md` | Cetak biru 5 seksi kuesioner pasca-tugas netral platform | Peneliti / Pengelola | **NO** | **NO** | **NO (Kode Saja)** | Spesifikasi Instrumen |
| 22 | `evaluation/e2/forms/E2_EXTERNAL_FORM_CONFIGURATION.md` | Panduan toggle setelan privasi platform survei digital | Pengelola Survei | **NO** | **NO** | **NO** | Panduan Konfigurasi Privasi |
| **E** | **BERKAS RUNTIME & SKRIP PENDUKUNG** | | | | | | |
| 23 | `evaluation/e2/runtime/db_session_template.sqlite3` | Basis data SQLite template murni tanpa baris data domain | Runtime Sesi | NO | NO | NO | Runtime Template Bersih |
| 24 | `evaluation/e2/runtime/dryrun_verification.py` | Skrip eksekusi simulasi dry-run deterministik & verifikasi scoring | Tim Peneliti | YES (Kunci Uji) | NO | NO (DRYRUN001) | Skrip Verifikasi Teknis |
| **F** | **TEMPLATE CSV BASIS DATA EVALUASI** | | | | | | |
| 25 | `evaluation/e2/templates/session_manifest.csv` | Template log manifes sesi, tautan berkas, & hash arsip database | Manajemen Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 26 | `evaluation/e2/templates/moderator_observation_template.csv` | Template rekaman tabular observasi tugas per peserta | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 27 | `evaluation/e2/templates/pilot_incident_log.csv` | Template pencatatan kendala teknis / deviasi sesi pilot | Manajemen Mutu | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 28 | `evaluation/e2/templates/participants.csv` | Template metadata subjek & demografi terkunci E1 | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 29 | `evaluation/e2/templates/task_results.csv` | Template kinerja penyelesaian tugas (keberhasilan & bantuan) | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 30 | `evaluation/e2/templates/comprehension_responses.csv` | Template respon kuis pemahaman objektif 8 butir | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 31 | `evaluation/e2/templates/sus_responses.csv` | Template rekaman mentah 10 butir System Usability Scale (SUS) | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 32 | `evaluation/e2/templates/perception_responses.csv` | Template respon 5 butir persepsi kejelasan alur kerja | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |
| 33 | `evaluation/e2/templates/qualitative_feedback.csv` | Template respon kualitatif 3 butir umpan balik terbuka | Analisis Data | NO | NO | NO (Kode Saja) | **Brankas B (Dataset Analisis Pseudonim)** |

---

### 3. Konfirmasi Integritas Pemisahan Berkas & Tata Kelola Privasi
Pemeriksaan tata kelola memverifikasi bahwa:
1. Direktori `materials/participant/` bersih 100% dari probabilitas, kontribusi GAM, kunci jawaban, dan rubrik bantuan moderator.
2. Seluruh kunci jawaban dan nilai acuan operasional terisolasi di direktori `materials/moderator/`.
3. **Pernyataan Privasi Langsung (*Direct PII Governance Claim*):**  
   Tidak ada PII langsung (*direct PII*) yang dikumpulkan dalam kuesioner analitis, rekaman alur kerja skrining/peninjauan antarmuka, dataset observasi moderator, atau ekspor analisis. Segala informasi identitas personal yang diperlukan untuk persetujuan keikutsertaan (*informed consent*) atau administrasi rekrutmen disimpan secara terpisah di bawah tata kelola administratif terbatas (Brankas A).
4. **Semantik Pseudonimitas:** Kode Peserta (*Participant Code*) adalah pengidentifikasi riset pseudonim (*pseudonymous research identifier*), bukan bukti anonimisasi ireversibel jika tautan identitas-kode masih tersimpan terpisah di Brankas A. Seluruh data riset selama masa studi diklasifikasikan sebagai data penelitian pseudonim.
5. **Akses Terbatas Brankas B:** Brankas B (Dataset Analisis Pseudonim / Terbatas) menyimpan rekaman pseudonim dengan akses terbatas untuk tim peneliti dan tidak bersifat terbuka/publik secara bebas.
