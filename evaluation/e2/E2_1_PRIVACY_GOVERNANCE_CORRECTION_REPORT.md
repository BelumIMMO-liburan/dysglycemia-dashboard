# Laporan Rekonsiliasi Tata Kelola Privasi & Klasifikasi PII Paket Pilot (Phase E2.1 Report)
## Rekonsiliasi Metadata Privasi, Klasifikasi Formulir Persetujuan, Terminologi Pseudonimitas, dan Arsitektur Dua Brankas

**Kode Dokumen:** `E2-1-PRIVACY-GOVERNANCE-REPORT-V1.0`  
**Fase Evaluasi:** `E2.1` (Privacy Metadata & Participant-Material Governance Reconciliation)  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Target Perangkat Lunak:** `research-prototype-v1.0` (Status: Terkunci / Frozen)  
**Status Gerbang Otorisasi:** 🔴 **NOT AUTHORIZED FOR PARTICIPANT CONTACT (TETAP TERKUNCI)**  
**Tanggal Pelaksanaan:** 2026-09-09  

---

### 1. Ringkasan Eksekutif & Kepatuhan Batasan Mutlak

Fase E2.1 merupakan fase rekonsiliasi tata kelola dokumentasi (*documentation and governance correction only*) yang bertujuan untuk mengoreksi inkonsistensi klasifikasi privasi dan metadata *Personally Identifiable Information* (PII) pada paket operasional pilot Fase E2.

Sesuai mandat pengawasan tata kelola riset (*Research Governance*), seluruh tindakan dalam fase ini tunduk pada batasan mutlak:
- **Perubahan Kode Sumber Prototipe (`research-prototype-v1.0`):** **0 berkas diubah** (kebekuan perangkat lunak terjaga 100%).
- **Perubahan Instrumen E1 & Skenario Tugas (Tasks 1–6):** **0 instrumen diubah** (protokol E1 tetap terkunci).
- **Kontak dengan Calon Partisipan:** **0 partisipan dihubungi** (tidak ada rekrutmen atau komunikasi subjek manusia).
- **Pengumpulan Data Manusia:** **0 data manusia dikumpulkan**.
- **Status Gerbang Otorisasi Pra-Pilot:** **TETAP TERTUTUP RAPAT (`NOT AUTHORIZED FOR PARTICIPANT CONTACT`)**.

---

### 2. Rekonsiliasi Klasifikasi PII Lembar Persetujuan (*Consent Form*)

#### 2.1 Identifikasi Masalah Klasifikasi Sebelumnya
Dokumentasi awal secara simplistis mengklasifikasikan seluruh materi peserta dengan label tunggal:
$$\text{Contains PII} = \text{NO}$$
Label tunggal ini ambigu dan tidak akurat karena formulir persetujuan keikutsertaan (*informed consent*) yang telah ditandatangani oleh subjek manusia secara inheren merekam identitas langsung subjek (tanda tangan dan persetujuan) yang ditautkan ke **Kode Peserta** (*Participant Code*) demi pemenuhan kepatuhan etik penelitian.

#### 2.2 Inventaris Kolom Faktual Formulir Persetujuan
Berdasarkan berkas asli [E2_CONSENT_FORM_DRAFT_ID.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/materials/participant/E2_CONSENT_FORM_DRAFT_ID.md), butir isian administratif yang diminta saat pelaksanaan sesi adalah:
1. **Kode Peserta yang Diberikan** (`reviewer_code` / `participant_code`, misal `PILOT001`)
2. **Tanggal Pelaksanaan Sesi**
3. **Tanda Tangan / Persetujuan Peserta**
4. **Nama Terang Peneliti / Moderator**
5. **Tanda Tangan Peneliti / Moderator**

*Catatan Kepatuhan:* Tidak ada penambahan kolom buatan (seperti NIK, nomor telepon, atau alamat rumah). Rekonsiliasi didasarkan secara murni pada kolom faktual dokumen.

#### 2.3 Skema Klasifikasi Privasi Empat Dimensi
Untuk mengeliminasi ambiguitas, formulir persetujuan dan seluruh instrumen kini dinilai melalui empat dimensi tata kelola yang tegas:

| Dimensi Tata Kelola Privasi | Status Formulir Persetujuan (`E2_CONSENT_FORM_DRAFT_ID.md`) | Justifikasi & Mekanisme Perlindungan |
| :--- | :---: | :--- |
| **A. Memuat PII Pra-Sesi pada Berkas Blanko?** | **TIDAK / NO** | Berkas draf/template kosong tidak memuat data identitas partisipan mana pun. |
| **B. Mengumpulkan PII Langsung Saat Diisi?** | **YA / YES** | Mengumpulkan tanda tangan dan konfirmasi persetujuan peserta yang bertaut dengan Kode Peserta untuk akuntabilitas etik. |
| **C. Domain Penyimpanan (*Storage Domain*)** | **Brankas A (Administratif Terbatas)** | Disimpan secara fisik/digital dalam map atau direktori terenkripsi terpisah dengan akses sangat terbatas (*Administrative Restricted Vault*). |
| **D. Termasuk dalam Dataset Analisis?** | **TIDAK / NO** | Terisolasi penuh dari basis data SQLite, berkas CSV analitis, dan repositori riset terbuka (*excluded from analytical dataset*). |

---

### 3. Pembaruan Skema Manifes Paket Pilot (`E2_PILOT_PACKAGE_MANIFEST.md`)

Kolom tunggal `Memuat PII?` yang ambigu pada manifes paket pilot telah digantikan dengan skema metadata tata kelola yang komprehensif:
- `Memuat Kunci Jawaban?` (Pemisahan materi peserta vs moderator)
- `Memuat PII Pra-Sesi?` (Integritas template blanko)
- `Mengumpulkan PII Saat Selesai?` (Pembedaan instrumen pengumpul tanda tangan etik vs instrumen evaluasi teknis)
- `Domain Penyimpanan & Analisis` (Penetapan lokasi brankas A vs B)

#### Rekapitulasi Audit 33 Artefak Paket E2:
1. **Materi Persetujuan Peserta (1 berkas):**  
   `E2_CONSENT_FORM_DRAFT_ID.md` diklasifikasikan: `PII Pra-Sesi = NO`, `Kumpul PII Selesai = YES (Tanda Tangan)`, `Domain = Brankas A (Administratif Terbatas, Terpisah dari Analisis)`.
2. **Materi Tugas & Informasi Peserta (6 berkas):**  
   `E2_PARTICIPANT_INFORMATION_SHEET_ID.md`, `E2_PARTICIPANT_TASK_BOOKLET_ID.md`, `E2_CASE_CARD_ALPHA_ID.md`, `E2_CASE_CARD_BETA_ID.md`, `E2_STAGE2_CASE_ALPHA_CARD_ID.md`, `E2_OVERRIDE_SCENARIO_BETA_ID.md` diklasifikasikan: `PII Pra-Sesi = NO`, `Kumpul PII Selesai = NO`, `Domain = Materi Operasional Peserta`.
3. **Materi Moderator & Peneliti (3 berkas):**  
   `E2_MODERATOR_EXPECTED_STATE_KEY.md` (memuat kunci jawaban), `E2_MODERATOR_OBSERVATION_SHEET.md` (hanya kode peserta, Brankas B), `E2_PILOT_MODERATOR_RUNBOOK.md` (panduan operasional). Seluruhnya `Kumpul PII = NO`.
4. **Formulir Kuesioner Digital Eksternal (2 berkas):**  
   `E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md` dan `E2_EXTERNAL_FORM_CONFIGURATION.md`. Wajib: `Kumpul PII = NO` (pengumpulan email dan login akun dimatikan; identitas responden murni diwakili oleh Kode Peserta).
5. **Runtime & Verifikasi (2 berkas):**  
   `db_session_template.sqlite3` dan `dryrun_verification.py`. Murni teknis/deterministik tanpa PII manusia.
6. **Template CSV Basis Data Studi (9 berkas):**  
   Seluruh 9 template CSV (`session_manifest`, `moderator_observation`, `pilot_incident_log`, `participants`, `task_results`, `comprehension_responses`, `sus_responses`, `perception_responses`, `qualitative_feedback`) diklasifikasikan: `PII Pra-Sesi = NO`, `Kumpul PII Selesai = NO (Kode Peserta Saja)`, `Domain = Brankas B (Dataset Analisis Pseudonim / Terbatas)`.
7. **Dokumen Tata Kelola & Arsitektur Utama (10 berkas):**  
   Dokumen acuan tata kelola, protokol database, dan gerbang otorisasi pra-pilot.

---

### 4. Semantik Pseudonimitas & Batasan Risiko Re-Identifikasi

Dokumentasi tata kelola telah direkonsiliasi untuk meluruskan terminologi de-identifikasi:

1. **Definisi Presisi Kode Peserta:**  
   **Kode Peserta (*Participant Code*)** adalah **pengidentifikasi riset pseudonim (*pseudonymous research identifier*)**, bukan bukti anonimisasi ireversibel (*irreversible anonymization*).
2. **Larangan Klaim "Anonim Mutlak" Selama Masa Studi:**  
   Selama tautan pemetaan administratif antara identitas subjek dan kode peserta masih tersimpan di Brankas A (demi audit etik atau bukti presensi), dataset penelitian di Brankas B **tidak boleh diklaim sebagai data yang sepenuhnya atau permanen anonim**. Dataset tersebut harus didefinisikan secara presisi sebagai **data penelitian pseudonim (*pseudonymous research data*)**.
3. **Siklus Hidup Retensi & Anonimisasi Pasca-Studi:**  
   Anonimisasi permanen hanya dapat tercapai setelah masa retensi penelitian dan kewajiban pertanggungjawaban sidang skripsi selesai, di mana berkas pemetaan identitas pada Brankas A dimusnahkan secara aman (*secure physical/digital destruction*) sesuai ketentuan komite etik institusi.

---

### 5. Koreksi Terminologi Brankas Analisis (*Analysis Vault Wording*)

Telah dilakukan koreksi formal terhadap penamaan Brankas B pada seluruh dokumen terkait:

- **Istilah Lama (Dihapus):**  
  `Brankas B (Dataset Analisis Terbuka)`
- **Istilah Rekonsiliasi (Ditetapkan):**  
  `Brankas B (Dataset Analisis Pseudonim / Terbatas)` atau `Vault B (Pseudonymous / Restricted Analytical Dataset)`

**Rasional Tata Kelola:**  
Penggunaan kata *"Terbuka"* (*Open*) memberikan implikasi keliru bahwa data respon dan riwayat evaluasi peserta dapat diakses oleh publik secara bebas. Faktanya, Brankas B adalah repositori penelitian dengan akses terbatas (*restricted access*) khusus bagi tim peneliti yang berwenang.

---

### 6. Arsitektur Dua Brankas (*Two-Vault Architecture*)

Pemisahan fisik dan logis yang ketat antara dua domain penyimpanan ditegaskan kembali:

```
+----------------------------------------------------------------------------------------------------+
|                                    ARSITEKTUR DUA BRANKAS (TWO-VAULT)                              |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    [ BRANKAS A: ADMINISTRATIF TERBATAS ]               [ BRANKAS B: DATASET ANALISIS PSEUDONIM ]    |
|    (Administrative Restricted Vault)                   (Restricted Pseudonymous Analytical Dataset) |
|    ─────────────────────────────────                   ───────────────────────────────────────────  |
|    • Lembar persetujuan (informed consent)             • Basis data SQLite per sesi (db_study)      |
|    • Tanda tangan fisik / konfirmasi subjek            • Ekspor respon kuesioner digital (CSV)      |
|    • Tautan identitas subjek ↔ Kode Peserta            • Lembar observasi tugas moderator (CSV)     |
|    • Disimpan di map fisik terkunci / direktori        • Manifes arsip sesi & hash SHA-256 (CSV)    |
|      administratif terenkripsi terpisah                • 100% bebas dari nama, NIM, email, & telp   |
|    • Akses terbatas pengelola etik                     • Akses tim peneliti terotorisasi            |
|    • EKSKLUSIF TERISOLASI DARI ANALISIS                • HANYA MEMUAT KODE PESERTA PSEUDONIM        |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
                                      ▲                                             ▲
                                      │                                             │
                                      └─── [ PEMISAHAN MUTLAK / ABSOLUTE BARRIER ] ─┘
                                           Kunci tautan identitas dilarang keras
                                           masuk ke dalam berkas ekspor analitis!
```

---

### 7. Koreksi Pernyataan Pengumpulan PII Langsung (*Direct PII Claim*)

Pernyataan simplistis seperti *"Tidak ada berkas yang mengumpulkan PII"* telah dikoreksi dan digantikan secara seragam dengan formulasi tata kelola standar:

> *"Tidak ada PII langsung (direct PII) yang dikumpulkan dalam kuesioner analitis, rekaman alur kerja skrining/peninjauan antarmuka, dataset observasi moderator, atau ekspor analisis. Segala informasi identitas personal yang diperlukan untuk persetujuan keikutsertaan (informed consent) atau administrasi rekrutmen disimpan secara terpisah di bawah tata kelola administratif terbatas (Brankas A)."*

Formulasi ini secara jujur mengakui adanya pengumpulan tanda tangan pada formulir persetujuan demi kepatuhan etik, sembari menegaskan bahwa seluruh alur kerja analitis bebas dari pencemaran PII langsung.

---

### 8. Penyelarasan Bahasa Skrining vs Alur Kerja Klinis

Sesuai panduan *Research Governance*, frasa yang mengimplikasikan pengujian alur kerja klinis medis dalam studi kegunaan prototipe perangkat lunak telah diselaraskan:

- **Frasa Lama:**  
  `"data bukti alur kerja klinis"`
- **Frasa Rekonsiliasi:**  
  `"data bukti alur kerja skrining/peninjauan (screening/review workflow data)"`

Penyelarasan ini diterapkan secara proporsional pada konteks evaluasi prototipe tugas akhir, tanpa mengubah konteks referensi klinis yang sah (seperti pedoman rujukan laboratorium HbA1c menurut standar medis American Diabetes Association).

---

### 9. Konfirmasi Integritas Verifikasi Dry-Run (DRYRUN001)

Hasil pengujian teknis deterministik `DRYRUN001` pada [E2_DATA_LINKAGE_DRYRUN_REPORT.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_DATA_LINKAGE_DRYRUN_REPORT.md) tetap **100% sah dan tidak diubah**:
- Temuan: **0 unintended PII** pada seluruh 7 CSV ekspor dan basis data SQLite arsip.
- Justifikasi: `DRYRUN001` merupakan simulasi non-human yang dieksekusi secara sintetis oleh peneliti, sehingga ketiadaan PII dalam uji coba tersebut merupakan bukti teknis yang valid atas keterisolasian skrip eksekusi dan template data.

---

### 10. Status Gerbang Otorisasi Pra-Pilot (*Authorization Gate*)

Dokumen kendali gerbang [E2_PRE_PILOT_AUTHORIZATION_GATE.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_PRE_PILOT_AUTHORIZATION_GATE.md) tetap berstatus:

🔴 **NOT AUTHORIZED FOR PARTICIPANT CONTACT**  
*(TIDAK DIIZINKAN UNTUK MENGHUBUNGI ATAU MEREKRUT PARTISIPAN)*

Seluruh butir persetujuan eksternal (persetujuan tertulis pembimbing, konfirmasi komite etik institusi, dan pengisian nomor protokol) tetap berstatus **PENDING** dan tidak dimodifikasi secara sepihak.

---

### 11. Matriks Berkas yang Direkonsiliasi dalam Fase E2.1

| No | Berkas yang Dimutakhirkan | Jenis Dokumen | Ringkasan Perubahan Tata Kelola |
| :-: | :--- | :--- | :--- |
| 1 | [E2_PILOT_PACKAGE_MANIFEST.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_PILOT_PACKAGE_MANIFEST.md) | Manifes Paket | Pembaruan skema metadata 4 dimensi privasi, audit 33 berkas, klasifikasi Brankas A untuk formulir persetujuan, dan adopsi pernyataan PII langsung standar. |
| 2 | [E2_PILOT_PREPARATION_REPORT.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_PILOT_PREPARATION_REPORT.md) | Laporan Kesiapan | Perubahan Brankas B menjadi Dataset Analisis Pseudonim / Terbatas, klasifikasi faktual consent form, penggunaan frasa *screening/review workflow data*, dan penegasan semantik kode peserta. |
| 3 | [E2_PARTICIPANT_CODE_SCHEME.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_PARTICIPANT_CODE_SCHEME.md) | Spesifikasi Kode | Penegasan Kode Peserta sebagai pengidentifikasi riset pseudonim (bukan bukti anonimisasi ireversibel), penataan batasan Brankas A vs B, dan siklus hidup anonimisasi pasca-studi. |
| 4 | [E2_HYBRID_COLLECTION_ARCHITECTURE.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_HYBRID_COLLECTION_ARCHITECTURE.md) | Arsitektur Sistem | Penyelarasan bahasa *screening/review workflow logs* dan adopsi pernyataan ketiadaan PII langsung dalam dataset analitis. |
| 5 | [E2_CONSENT_FORM_DRAFT_ID.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/materials/participant/E2_CONSENT_FORM_DRAFT_ID.md) | Draf Persetujuan | Penambahan blok klasifikasi tata kelola privasi 4 dimensi di header dan penegasan semantik pengidentifikasi riset pseudonim pada butir 6. |
| 6 | [E2_PARTICIPANT_INFORMATION_SHEET_ID.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/materials/participant/E2_PARTICIPANT_INFORMATION_SHEET_ID.md) | Informasi Peserta | Penegasan Kode Peserta sebagai pengidentifikasi riset pseudonim, Brankas B sebagai dataset analisis terbatas, dan Brankas A untuk berkas persetujuan. |
| 7 | [E2_PILOT_EXECUTION_CHECKLIST.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_PILOT_EXECUTION_CHECKLIST.md) | Daftar Periksa | Penegasan penyimpanan lembar persetujuan di Brankas A terisolasi dan verifikasi nol PII langsung di berkas analitis Brankas B. |
| 8 | [E2_PILOT_MODERATOR_RUNBOOK.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/materials/moderator/E2_PILOT_MODERATOR_RUNBOOK.md) | Runbook Moderator | Penegasan pemisahan Brankas A (Administrasi Terbatas) dan Brankas B (Dataset Analisis) pada instruksi langkah 5. |
| 9 | [E2_1_PRIVACY_GOVERNANCE_CORRECTION_REPORT.md](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_1_PRIVACY_GOVERNANCE_CORRECTION_REPORT.md) | Laporan Penutupan | Pembuatan laporan komprehensif penutupan Fase E2.1 ini. |

---

### 12. Konfirmasi Metrik Tata Kelola Akhir

- **Perubahan Prototipe (`research-prototype-v1.0`):** `0`
- **Kontak Partisipan Manusia:** `0`
- **Data Manusia Dikumpulkan:** `0`
- **Status Gerbang Otorisasi:** `CLOSED (TIDAK BERUBAH)`

---

PHASE E2.1 COMPLETE — PILOT PACKAGE PRIVACY CLASSIFICATION RECONCILED WITHOUT PARTICIPANT CONTACT
