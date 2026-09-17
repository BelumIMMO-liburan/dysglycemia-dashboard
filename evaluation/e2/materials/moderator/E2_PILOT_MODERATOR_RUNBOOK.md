# Petunjuk Teknis Pelaksanaan Moderator (Moderator Runbook)
## Panduan Operasional Sesi Evaluasi Antarmuka Skrining Risiko Disglikemia Dua Tahap

**Kode Dokumen:** `E2-MOD-RUNBOOK-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tingkat Kerahasiaan:** **PENELITI / MODERATOR SAJA**  

---

### 1. Prinsip Dasar Peran Moderator
- **Objektivitas:** Moderator bertindak sebagai fasilitator netral, bukan pengajar (*instructor*) atau pembela sistem.
- **Standarisasi Instruksi:** Moderator dilarang memberikan improvisasi petunjuk atau penjelasan mekanika AI sebelum peserta menyelesaikan tugas mandirinya.
- **Kepatuhan Protokol:** Seluruh urutan 13 langkah di bawah ini wajib diikuti secara disiplin untuk menjamin validitas internal evaluasi.

---

### 2. Prosedur 13 Langkah Pelaksanaan Sesi

```
[Tahap 1: Otorisasi] -> [Tahap 2: Reset DB] -> [Tahap 3: Alokasi Kode] -> [Tahap 4: Lembar Info]
        |
[Tahap 5: Informed Consent] -> [Tahap 6: Orientasi] -> [Tahap 7: Pengerjaan Tugas 1-6]
        |
[Tahap 8: Pencatatan Observasi] -> [Tahap 9: Kuesioner Tertutup] -> [Tahap 10: Debriefing]
        |
[Tahap 11: Pengarsipan & Hash] -> [Tahap 12: Audit Keterhubungan] -> [Tahap 13: Penyiapan DB Bersih]
```

---

#### TAHAP 1: Verifikasi Gerbang Otorisasi Pra-Pilot (*Pre-Pilot Authorization Check*)
1. Periksa dokumen `E2_PRE_PILOT_AUTHORIZATION_GATE.md`.
2. Pastikan status gerbang telah bertuliskan: **AUTHORIZED FOR PILOT CONTACT**.
3. Jika status masih *NOT AUTHORIZED* atau persetujuan pembimbing/etik belum lengkap: **HENTIKAN SESI. DILARANG MENGHUBUNGI ATAU MENGUMPULKAN DATA DARI PARTISIPAN MANUSIA.**

#### TAHAP 2: Penyiapan Isolasi Basis Data Sesi (*Session Database Isolation*)
1. Pastikan server prototipe sedang dalam keadaan mati (*quiesced / stopped*).
2. Salin template bersih `evaluation/e2/runtime/db_session_template.sqlite3` ke file kerja aktif `dashboard/db_study.sqlite3`.
3. Jalankan verifikasi hitungan nol baris (*zero-count verification*):
   - `ScreeningRecord` = 0
   - `ScreeningExplanation` = 0
   - `HumanReview` = 0
   - `Stage2Assessment` = 0
4. Nyalakan server aplikasi: `py -3.10 manage.py runserver 8000`.

#### TAHAP 3: Penetapan Kode Peserta (*Participant Code Assignment*)
1. Tentukan kode peserta sesuai urutan:
   - Untuk Sesi Pilot Feasibilitas: `PILOT001`, `PILOT002`, `PILOT003`, dst.
   - Untuk Sesi Studi Formal (Masa Depan): `P001`, `P002`, dst.
2. Tuliskan kode tersebut pada Lembar Observasi Moderator, lembar kendali berkas, dan siapkan pada kartu pengenal meja.
3. Pastikan tidak ada pencatatan nama subjek di lembar observasi maupun platform kuesioner analitis.

#### TAHAP 4: Penjelasan Lembar Informasi Peserta (*Participant Information*)
1. Serahkan lembar cetak `E2_PARTICIPANT_INFORMATION_SHEET_ID.md` kepada peserta.
2. Berikan waktu 5–10 menit bagi peserta untuk membaca informasi penelitian.
3. Tegaskan poin-poin utama:
   - Sistem ini adalah prototipe penelitian, **bukan alat diagnosis klinis**.
   - Data kasus yang digunakan adalah **kasus sintetis/fiktif**.
   - Partisipasi bersifat sukarela dan peserta berhak berhenti kapan saja.

#### TAHAP 5: Penandatanganan Lembar Persetujuan (*Informed Consent*)
1. Serahkan formulir draf persetujuan `E2_CONSENT_FORM_DRAFT_ID.md`.
2. Berikan kesempatan kepada peserta untuk mengajukan pertanyaan jika ada yang belum jelas.
3. Minta peserta mencentang persetujuan dan menandatangani formulir persetujuan fisik.
4. Simpan formulir persetujuan yang telah ditandatangani ke dalam Brankas Administrasi Fisik (Brankas A - Administratif Terbatas, terisolasi penuh dari dataset analisis Brankas B).

#### TAHAP 6: Orientasi Standar Antarmuka (*Standardized Interface Orientation*)
1. Tampilkan halaman muka sistem (*Dashboard Overview*) pada layar peramban web.
2. Sampaikan teks orientasi standar berikut (jangan improvisasi):
   > *"Selamat datang. Di hadapan Anda adalah prototipe sistem antarmuka skrining risiko disglikemia dua tahap. Di sisi kiri terdapat menu navigasi utama yang mencakup New Screening untuk menginput data baru, dan History untuk melihat riwayat kasus. Anda akan diminta menyelesaikan serangkaian tugas sesuai instruksi pada buku panduan. Silakan bekerja dengan kecepatan wajar Anda."*
3. Jangan menunjukkan letak tombol aksi khusus atau trik navigasi sebelum tugas dimulai.

#### TAHAP 7: Pelaksanaan Tugas 1 s.d. 6 (*Tasks Execution*)
1. Serahkan Buku Panduan Tugas Peserta (`E2_PARTICIPANT_TASK_BOOKLET_ID.md`), Kartu Kasus Alpha (`E2_CASE_CARD_ALPHA_ID.md`), Kartu Kasus Beta (`E2_CASE_CARD_BETA_ID.md`), Kartu Alpha Tahap-2 (`E2_STAGE2_CASE_ALPHA_CARD_ID.md`), dan Kartu Override Beta (`E2_OVERRIDE_SCENARIO_BETA_ID.md`).
2. Pandu peserta memulai dari Tugas 1 hingga Tugas 6 sesuai instruksi tertulis.
3. Catat waktu mulai dan waktu selesai jika mencatat durasi tugas.

#### TAHAP 8: Pencatatan Lembar Observasi Moderator (*Observation Logging*)
1. Amati interaksi peserta dari posisi yang tidak mengintimidasi (duduk di samping/belakang dengan jarak wajar).
2. Terapkan rubrik bantuan secara ketat:
   - Jika peserta ragu tetapi tidak bertanya, biarkan mencoba mandiri (Level 0).
   - Jika peserta bertanya arti instruksi, ulangi kalimat pada buku tugas (Level 1).
   - Jika peserta tersesat lebih dari 60 detik tanpa arah, tunjukkan area menu terkait (Level 2).
   - Jika peserta macet total dan meminta bantuan teknis, tunjukkan klik yang diperlukan (Level 3).
3. Tandai centang pada `E2_MODERATOR_OBSERVATION_SHEET.md` secara terstruktur per tugas.

#### TAHAP 9: Pengisian Kuesioner Mandiri Tertutup (*Closed-Book Questionnaire*)
1. Setelah Tugas 6 selesai, minta peserta menutup jendela prototipe antarmuka atau beralih tab ke platform kuesioner digital.
2. Instruksikan secara lisan:
   > *"Terima kasih telah menyelesaikan tugas antarmuka. Sekarang silakan membuka tautan kuesioner berikut. Sesuai protokol penelitian, bagian pemahaman objektif ini bersifat tertutup (closed-book), sehingga kami mohon untuk tidak membuka kembali halaman prototipe antarmuka selama pengisian berlangsung."*
3. Pastikan field pertama kuesioner diisi persis dengan **Kode Peserta** yang sama (mis. `PILOT001`).
4. Pastikan peserta mengisi seluruh 8 butir pemahaman, 10 butir SUS, 5 butir kejelasan, dan 3 umpan balik terbuka.

#### TAHAP 10: Penutupan dan Tanya-Jawab Sesi (*Debriefing*)
1. Konfirmasi bahwa pengiriman respon kuesioner telah berhasil di layar (*Submission Successful*).
2. Ucapkan terima kasih atas partisipasi peserta.
3. Berikan apresiasi/kompensasi (jika diatur dalam protokol formal).
4. Jika peserta memiliki pertanyaan mengenai sistem atau hasil penelitian, berikan penjelasan edukatif penutup.

#### TAHAP 11: Pengarsipan Basis Data dan Perhitungan Hash (*Archive & Hash*)
1. Hentikan server prototipe.
2. Salin basis data aktif `dashboard/db_study.sqlite3` ke direktori arsip sesi:
   `evaluation/pilot_data/sessions/<PARTICIPANT_CODE>/<PARTICIPANT_CODE>_dashboard.sqlite3`
3. Hitung nilai *checksum SHA-256* dari file basis data yang diarsipkan:
   `Get-FileHash <PARTICIPANT_CODE>_dashboard.sqlite3 -Algorithm SHA256`
4. Catat nilai SHA-256 pada catatan manifes sesi.

#### TAHAP 12: Verifikasi Keterhubungan Kode Peserta (*Data Linkage Audit*)
1. Verifikasi bahwa Kode Peserta yang sama tertera persis di:
   - [ ] Basis data `HumanReview.reviewer_code` (pada 2 record: Alpha & Beta)
   - [ ] Berkas Observasi Moderator (`<PARTICIPANT_CODE>_moderator.csv`)
   - [ ] Baris Ekspor Kuesioner Digital (`<PARTICIPANT_CODE>_survey.csv`)
   - [ ] Baris Manifes Sesi (`session_manifest.csv`)
2. Periksa bahwa jumlah baris pada basis data sesi tepat: 2 record skrining, 2 penjelasan, 2 peninjauan manusia, 1 rekam tahap-2.

#### TAHAP 13: Penyiapan Kembali Basis Data Bersih (*Fresh Environment Reset*)
1. Hapus atau bersihkan `dashboard/db_study.sqlite3`.
2. Salin kembali template bersih `evaluation/e2/runtime/db_session_template.sqlite3` menjadi `dashboard/db_study.sqlite3`.
3. Verifikasi hitungan nol baris untuk menjamin riwayat peserta sebelumnya tidak terlihat oleh peserta berikutnya.
