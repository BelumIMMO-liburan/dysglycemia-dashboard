# Daftar Periksa Pelaksanaan Sesi Pilot (Pilot Execution Checklist)
## Kontrol Kualitas Operasional Sesi Pengujian Kelayakan ($N=3\text{--}5$)

**Kode Dokumen:** `E2-PILOT-CHECKLIST-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Peringatan:** Daftar periksa ini disiapkan untuk pelaksanaan pilot masa depan. Dilarang dijalankan dengan partisipan manusia sebelum gerbang otorisasi dibuka.

---

### I. FASE SEBELUM SESI (PRE-SESSION PREPARATION)

#### 1. Verifikasi Tata Kelola & Otorisasi
- [ ] Dokumen `E2_PRE_PILOT_AUTHORIZATION_GATE.md` telah berstatus **AUTHORIZED FOR PILOT CONTACT**.
- [ ] Surat persetujuan pembimbing dan/atau bukti kaji etik telah diarsipkan dalam brankas administrasi.

#### 2. Integritas Perangkat Lunak & Lingkungan
- [ ] Versi aplikasi terverifikasi: `research-prototype-v1.0` (tidak ada perubahan kode/model).
- [ ] Integritas 4 berkas riset terlindung terverifikasi (GAM, Preprocessor, Spec, Test Predictions).
- [ ] Peramban web bersih dari riwayat / *cache* sesi sebelumnya.

#### 3. Isolasi Basis Data Sesi (Zero-State Database Check)
- [ ] File template `evaluation/e2/runtime/db_session_template.sqlite3` disalin ke `dashboard/db_study.sqlite3`.
- [ ] Skrip verifikasi dijalankan:
  - `ScreeningRecord.objects.count() == 0`
  - `ScreeningExplanation.objects.count() == 0`
  - `HumanReview.objects.count() == 0`
  - `Stage2Assessment.objects.count() == 0`
- [ ] Aplikasi dijalankan pada port lokal terisolasi (`APP_DATA_MODE=study`).

#### 4. Kesiapan Materi Cetak & Kartu Skenario
- [ ] Lembar Informasi Peserta (`E2_PARTICIPANT_INFORMATION_SHEET_ID.md`) tercetak rapi.
- [ ] Lembar Persetujuan (*Informed Consent*) (`E2_CONSENT_FORM_DRAFT_ID.md`) tercetak.
- [ ] Buku Panduan Tugas Peserta (`E2_PARTICIPANT_TASK_BOOKLET_ID.md`) tercetak tanpa kebocoran kunci jawaban.
- [ ] Kartu Kasus Alpha (`E2_CASE_CARD_ALPHA_ID.md`) siap.
- [ ] Kartu Kasus Beta (`E2_CASE_CARD_BETA_ID.md`) siap.
- [ ] Kartu Alpha Tahap-2 (`E2_STAGE2_CASE_ALPHA_CARD_ID.md`) siap.
- [ ] Kartu Instruksi Override Beta (`E2_OVERRIDE_SCENARIO_BETA_ID.md`) siap.
- [ ] Lembar Observasi Moderator (`E2_MODERATOR_OBSERVATION_SHEET.md`) telah tercetak dan terisi Kode Peserta.

#### 5. Kesiapan Formulir Kuesioner Digital
- [ ] Tautan formulir eksternal aktif dan dapat diakses dari komputer uji.
- [ ] Pengaturan privasi diverifikasi: Pengumpulan email MATI, wajib login MATI.
- [ ] Validasi format *Participant Code* berfungsi.

---

### II. FASE SELAMA SESI (IN-SESSION EXECUTION)

#### 1. Penerimaan & Persetujuan
- [ ] Penjelasan lisan ringkas tujuan penelitian dan sifat prototipe non-medis.
- [ ] Peserta membaca Lembar Informasi dan menandatangani Lembar Persetujuan.
- [ ] Formulir persetujuan disimpan dalam map fisik terpisah (Brankas A Administratif Terbatas, terisolasi penuh dari data analisis).

#### 2. Orientasi Sistem
- [ ] Moderator menyampaikan narasi orientasi standar selama 5 menit tanpa membeberkan trik navigasi.

#### 3. Pelaksanaan Tugas 1 s.d. 6
- [ ] Tugas 1 (Input Case Alpha): Nilai 7 parameter diisi sesuai kartu.
- [ ] Tugas 2 (Hasil & XAI Alpha): Peserta membuka 7 faktor dan mengidentifikasi arah faktor.
- [ ] Tugas 3 (Human Review Alpha): Peserta memasukkan kode peserta dan menyetujui rekomendasi (*Accept*).
- [ ] Tugas 4 (Override Case Beta): Peserta memasukkan Case Beta, membuka modal override, memilih alasan terstruktur baku, memasukkan catatan skenario, dan menyimpan.
- [ ] Tugas 5 (Stage-2 Alpha): Peserta membuka kembali Alpha, menginput HbA1c 6.1%, mengonfirmasi hasil, dan mengamati rentang prediabetes.
- [ ] Tugas 6 (Riwayat Case Beta): Peserta memeriksa menu History, memverifikasi keterlacakan rekomendasi awal AI yang permanen, dan mencatat status Tahap-2 pending.
- [ ] Moderator mencatat hasil per tugas pada lembar observasi sesuai rubrik bantuan (Level 0–3).

#### 4. Pengisian Kuesioner Tertutup (Closed-Book Survey)
- [ ] Jendela prototipe diminimalkan / ditutup; peserta dilarang melihat kembali antarmuka.
- [ ] Peserta mengisi Kode Peserta yang persis sama pada kuesioner.
- [ ] Peserta menyelesaikan 8 butir kuis pemahaman objektif secara mandiri.
- [ ] Peserta menyelesaikan 10 butir SUS bahasa Indonesia.
- [ ] Peserta menyelesaikan 5 butir persepsi kejelasan alur.
- [ ] Peserta menyelesaikan 3 butir pertanyaan terbuka.
- [ ] Pengiriman respon formulir terkonfirmasi berhasil di layar.

---

### III. FASE SETELAH SESI (POST-SESSION ARCHIVAL & AUDIT)

#### 1. Pengarsipan Basis Data Sesi
- [ ] Server aplikasi dimatikan secara aman (*quiesced*).
- [ ] File `dashboard/db_study.sqlite3` disalin ke arsip sesi:
  `evaluation/pilot_data/sessions/<KODE_PESERTA>/<KODE_PESERTA>_dashboard.sqlite3`
- [ ] Nilai hash SHA-256 dihitung dan dicatat pada manifes.
- [ ] File basis data aktif tidak boleh digunakan kembali untuk sesi peserta berikutnya.

#### 2. Verifikasi Keterhubungan Kode (Linkage Audit)
- [ ] Kode Peserta identik pada keempat artefak sesi:
  1. `HumanReview.reviewer_code` dalam SQLite (2 baris: Alpha & Beta)
  2. Lembar Observasi Moderator (`<KODE>_moderator.csv`)
  3. Baris Ekspor Kuesioner Digital (`<KODE>_survey.csv`)
  4. Baris Manifes Sesi (`session_manifest.csv`)
- [ ] Tidak ada nama atau informasi identitas langsung (PII) yang tercampur dalam berkas analitis (Brankas B). Seluruh dataset analitis murni menggunakan Kode Peserta pseudonim.

#### 3. Log Insiden & Catatan Teknis
- [ ] Jika terjadi kendala sistem atau peramban web, catat segera pada `pilot_incident_log.csv`.
- [ ] Catat deviasi prosedur atau ketidakjelasan instruksi tugas (jika ada).

#### 4. Penyiapan Ulang Lingkungan Bersih (Reset Environment)
- [ ] Salin kembali `db_session_template.sqlite3` menjadi `db_study.sqlite3` baru.
- [ ] Verifikasi hitungan nol baris (*zero-count*) selesai dilakukan untuk menyambut peserta berikutnya.
