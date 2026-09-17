# Cetak Biru Kuesioner Evaluasi Eksternal (External Questionnaire Blueprint)
## Instrumen Pengukuran Pasca-Tugas: Pemahaman Objektif, SUS, Kejelasan Alur, & Umpan Balik

**Kode Dokumen:** `E2-SURVEY-BLUEPRINT-ID-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Bahasa Instrumen:** Bahasa Indonesia  
**Sifat Dokumen:** Spesifikasi Netral Platform (*Platform-Agnostic Survey Blueprint*)  
**Pemberitahuan Tata Kelola:**  
Instrumen ini diselenggarakan di luar aplikasi web prototipe (*decoupled external survey*) pada platform formulir digital yang disetujui institusi. Kuesioner ini dirancang untuk diisi secara tertutup (*closed-book*) segera setelah peserta menyelesaikan Tugas 1–6.

---

## STRUKTUR UMUM KUESIONER (5 SEKSI)

```
[SEKSI 1: Kode Peserta & Demografi Terkunci]
                ↓
[SEKSI 2: Kuis Pemahaman Objektif 8 Butir (Tertutup)]
                ↓
[SEKSI 3: System Usability Scale (SUS) 10 Butir Bahasa Indonesia]
                ↓
[SEKSI 4: Butir Persepsi Kejelasan Alur Kerja 5 Butir]
                ↓
[SEKSI 5: Umpan Balik Terbuka 3 Butir]
```

---

## SEKSI 1: IDENTIFIKATOR PESERTA & PROFIL PENGGUNA TERKUNCI

> **PANDUAN PRIVASI:**  
> Dilarang menambahkan kolom Nama Lengkap, Nomor Induk Mahasiswa/Karyawan, Alamat Email Pribadi, atau Nomor Telepon pada kuesioner ini. Identifikasi subjek hanya menggunakan Kode Peserta.

### 1.1 Kode Peserta (*Participant Code*)
- **Tipe Pertanyaan:** Teks Singkat (*Short Text*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Masukkan Kode Peserta Anda (sebagaimana diberikan oleh tim peneliti/moderator):"*
- **Format Validasi:** Pola RegEx `^(PILOT[0-9]{3}|P[0-9]{3}|DRYRUN[0-9]{3})$`
- **Contoh Isian:** `PILOT001`, `PILOT002`, `P001`
- **Pesan Galat Validasi:** *"Mohon masukkan format kode peserta yang valid (contoh: PILOT001 atau P001)."*

### 1.2 Kelompok Peserta (*Participant Group*)
- **Tipe Pertanyaan:** Pilihan Tunggal (*Radio Button*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Kelompok Partisipan:"*
- **Pilihan Jawaban:**
  - `primary` : Pengguna Utama / Mahasiswa / Masyarakat Umum
  - `expert` : Tenaga Kesehatan / Klinisi / Pakar

### 1.3 Rentang Usia (*Age Band*)
- **Tipe Pertanyaan:** Pilihan Tunggal (*Radio Button*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Rentang Usia Anda saat ini:"*
- **Pilihan Jawaban:**
  - `18-24` : 18 – 24 tahun
  - `25-34` : 25 – 34 tahun
  - `35-49` : 35 – 49 tahun
  - `50+` : 50 tahun ke atas

### 1.4 Tingkat Pendidikan Terakhir / Sedang Ditempuh (*Education Category*)
- **Tipe Pertanyaan:** Pilihan Tunggal (*Radio Button*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Pendidikan terakhir atau jenjang studi yang sedang ditempuh:"*
- **Pilihan Jawaban:**
  - `high_school` : SMA / SMK / Sederajat
  - `undergrad` : Sarjana Terapan / Mahasiswa S1
  - `bachelor` : Lulusan Sarjana (S1 / D4)
  - `postgrad` : Magister (S2) / Spesialis / Doktoral (S3)

### 1.5 Pengalaman Menggunakan Dashboard / Aplikasi Data (*Prior Dashboard Exp*)
- **Tipe Pertanyaan:** Pilihan Tunggal (*Radio Button*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Seberapa sering Anda menggunakan dashboard data atau antarmuka analitik komputer dalam aktivitas sehari-hari?"*
- **Pilihan Jawaban:**
  - `none` : Tidak pernah / Belum pernah
  - `occasional` : Kadang-kadang (1–2 kali per bulan)
  - `frequent` : Sering / Rutin (mingguan atau harian)

### 1.6 Latar Belakang Pendidikan / Pekerjaan di Bidang Kesehatan (*Health Background*)
- **Tipe Pertanyaan:** Pilihan Tunggal (*Radio Button*)
- **Status:** **WAJIB DIISI (Required)**
- **Teks Pertanyaan:** *"Apakah Anda memiliki latar belakang studi atau pekerjaan di bidang kesehatan/medis?"*
- **Pilihan Jawaban:**
  - `none` : Tidak memiliki latar belakang bidang kesehatan
  - `student` : Mahasiswa rumpun ilmu kesehatan (Kedokteran, Keperawatan, Gizi, Farmasi, Kesmas)
  - `practitioner` : Tenaga kesehatan / Dokter / Praktisi klinis aktif

---

## SEKSI 2: KUIS PEMAHAMAN OBJEKTIF (8 BUTIR PILIHAN GANDA TERTUTUP)

> **PETUNJUK ADMINISTRASI UNTUK PLATFORM:**  
> - Seluruh 8 butir pertanyaan di bawah ini berstatus **WAJIB DIISI (Required)**.
> - **JANGAN** aktifkan opsi acak urutan butir (*do not shuffle question order*).
> - **JANGAN** tampilkan kunci jawaban benar, pembahasan, atau skor langsung kepada peserta selama administrasi.
> - Penilaian skor dilakukan secara *offline* oleh peneliti pasca-ekspor.

### Butir 1 (`COMP_01` - Arti Sinyal Skrining vs Diagnosis)
- **Teks Soal:** Ketika dashboard menampilkan **"Elevated Screening Signal"** (Sinyal Skrining Meningkat) untuk sebuah profil skrining sintetis, apakah arti dari hasil tersebut?
- **Pilihan Jawaban:**
  - [A] Individu tersebut telah didiagnosis menderita diabetes oleh sistem.
  - [B] Model skrining statistik memperkirakan probabilitas di atas ambang batas rujukan, merekomendasikan penilaian laboratorium HbA1c Tahap-2.
  - [C] Individu tersebut dipastikan akan mengalami komplikasi diabetes dalam satu tahun ke depan.
  - [D] Laboratorium telah mengonfirmasi peningkatan kadar glukosa darah.

### Butir 2 (`COMP_02` - Arti Sinyal Skrining Rendah)
- **Teks Soal:** Jika sebuah profil skrining sintetis menerima **"Lower Screening Signal"** (Sinyal Skrining Lebih Rendah / Rekomendasi AI: Tidak Perlu Rujukan), apakah artinya?
- **Pilihan Jawaban:**
  - [A] Individu tersebut sepenuhnya bebas diabetes dan tidak akan pernah memerlukan skrining lagi.
  - [B] Estimasi probabilitas skrining individu berada di bawah ambang keputusan, sehingga rujukan laboratorium lanjutan saat ini tidak direkomendasikan.
  - [C] Pemeriksaan darah laboratorium menunjukkan kadar glukosa yang sepenuhnya normal.
  - [D] Individu tersebut memiliki probabilitas biologis 0,0% terhadap disglikemia.

### Butir 3 (`COMP_03` - Arah Kontribusi Faktor XAI)
- **Teks Soal:** Pada bagian **"Why this result?"** (Mengapa hasil ini?), apakah artinya jika sebuah faktor (seperti Usia) terdaftar di bawah **"Pushes screening score higher"** (Mendorong skor skrining lebih tinggi)?
- **Pilihan Jawaban:**
  - [A] Bahwa faktor input tersebut secara matematis meningkatkan skor skrining terhitung model statistik dalam perhitungan aditif.
  - [B] Bahwa faktor tersebut terbukti secara medis menyebabkan diabetes pada individu ini.
  - [C] Bahwa individu tersebut harus segera menjalani tindakan medis terkait faktor tersebut.
  - [D] Bahwa faktor tersebut adalah satu-satunya faktor yang diperhitungkan oleh model komputer.

### Butir 4 (`COMP_04` - Batasan Kausalitas Penjelasan)
- **Teks Soal:** Apakah grafik penjelasan faktor membuktikan bahwa suatu faktor input model tertentu menyebabkan kondisi metabolik individu tersebut?
- **Pilihan Jawaban:**
  - [A] Ya, karena model machine learning menemukan penyebab biologis yang sebenarnya.
  - [B] Ya, jika faktor tersebut berada di posisi teratas dalam peringkat.
  - [C] Tidak; grafik tersebut menampilkan asosiasi statistik dan kontribusi aditif model, bukan bukti klinis sebab-akibat biologis.
  - [D] Ya, karena data bersumber dari survei statistik kesehatan nasional.

### Butir 5 (`COMP_05` - Semantik Human Override)
- **Teks Soal:** Ketika seorang peninjau melakukan **"Human Override"** (Pengesampingan Manusia) dari "No Referral" menjadi "Refer", apa yang sebenarnya berubah di dalam sistem?
- **Pilihan Jawaban:**
  - [A] Model statistik menghitung ulang dan menaikkan nilai probabilitas AI.
  - [B] Keputusan akhir rujukan manusia diperbarui, sedangkan perhitungan asli AI tetap tersimpan tanpa perubahan dalam catatan audit.
  - [C] Kadar gula darah biologis individu tersebut berubah.
  - [D] Model machine learning di belakang sistem dilatih ulang secara permanen dengan keputusan baru tersebut.

### Butir 6 (`COMP_06` - Arti Rentang Laboratorium Tahap-2)
- **Teks Soal:** Ketika nilai HbA1c 6,6% dimasukkan pada Tahap 2 dan menampilkan **"Diabetes range"** (Rentang diabetes), apakah status dari hasil keluaran ini?
- **Pilihan Jawaban:**
  - [A] Ini adalah diagnosis medis otomatis dan mengikat secara hukum yang diterbitkan oleh prototipe.
  - [B] Ini menampilkan kategorisasi rentang laboratorium HbA1c berdasarkan kriteria acuan protokol (panduan standar ADA), yang tetap memerlukan interpretasi klinis.
  - [C] Ini adalah prediksi AI baru yang dihasilkan oleh jaringan saraf tiruan (neural network).
  - [D] Ini menandakan bahwa model Tahap-1 benar 100%.

### Butir 7 (`COMP_07` - Keabadian Rekomendasi Mesin & Jejak Audit)
- **Teks Soal:** Setelah Peninjau Manusia mengesampingkan (*override*) rekomendasi AI dan menyimpan data, apa yang terjadi pada rekomendasi awal mesin di riwayat kasus?
- **Pilihan Jawaban:**
  - [A] Dihapus secara permanen agar tidak membingungkan.
  - [B] Ditimpa dan digantikan oleh pilihan peninjau manusia.
  - [C] Tetap tercatat secara permanen dan terlihat dalam jejak audit bersama dengan alasan override dan kode peninjau.
  - [D] Disembunyikan dan hanya dapat diakses oleh administrator basis data.

### Butir 8 (`COMP_08` - Tingkat Kesepakatan Manusia-AI vs Akurasi Klinis)
- **Teks Soal:** Ketika analitik riset melaporkan **"Human–AI Agreement Rate"** (Tingkat Kesepakatan Manusia-AI) sebesar 85%, apakah arti dari persentase tersebut?
- **Pilihan Jawaban:**
  - [A] Bahwa model AI membuat diagnosis medis yang benar secara klinis pada 85% kasus.
  - [B] Bahwa peninjau manusia menyetujui rekomendasi rujukan AI pada 85% skrining yang ditinjau.
  - [C] Bahwa sensitivitas klinis model tepat bernilai 85%.
  - [D] Bahwa 85% individu yang diskrining dalam basis data terkonfirmasi menderita diabetes.

---

## SEKSI 3: SYSTEM USABILITY SCALE (SUS) — ADAPTASI INDONESIA
*(Sharfina & Santoso, 2016)*

> **PANDUAN SKALA:**  
> - Skala 5-poin Likert:
>   - `1` = Sangat Tidak Setuju
>   - `2` = Tidak Setuju
>   - `3` = Ragu-ragu / Netral
>   - `4` = Setuju
>   - `5` = Sangat Setuju
> - Seluruh 10 butir berstatus **WAJIB DIISI (Required)**.
> - Urutan butir ganjil (+) dan genap (-) dipertahankan secara bergantian.
> - Dilarang menampilkan perhitungan skor SUS kepada responden.

| Kode Butir | Polaritas | Teks Pernyataan (Bahasa Indonesia Baku) | Skala Pilihan |
| :---: | :---: | :--- | :---: |
| **SUS_01** | Ganjil (+) | Saya berpikir bahwa saya ingin sering menggunakan sistem ini. | 1 – 2 – 3 – 4 – 5 |
| **SUS_02** | Genap (-) | Saya merasa sistem ini rumit untuk digunakan. | 1 – 2 – 3 – 4 – 5 |
| **SUS_03** | Ganjil (+) | Saya merasa sistem ini mudah digunakan. | 1 – 2 – 3 – 4 – 5 |
| **SUS_04** | Genap (-) | Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini. | 1 – 2 – 3 – 4 – 5 |
| **SUS_05** | Ganjil (+) | Saya merasa fungsi-fungsi dalam sistem ini bekerja dengan baik. | 1 – 2 – 3 – 4 – 5 |
| **SUS_06** | Genap (-) | Saya merasa ada banyak hal yang tidak konsisten pada sistem ini. | 1 – 2 – 3 – 4 – 5 |
| **SUS_07** | Ganjil (+) | Saya merasa bahwa orang lain akan memahami cara menggunakan sistem ini dengan cepat. | 1 – 2 – 3 – 4 – 5 |
| **SUS_08** | Genap (-) | Saya merasa sistem ini membingungkan. | 1 – 2 – 3 – 4 – 5 |
| **SUS_09** | Ganjil (+) | Saya merasa tidak ada hambatan dalam menggunakan sistem ini. | 1 – 2 – 3 – 4 – 5 |
| **SUS_10** | Genap (-) | Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini. | 1 – 2 – 3 – 4 – 5 |

---

## SEKSI 4: BUTIR PERSEPSI KEJELASAN ALUR KERJA (5 BUTIR EKSPLORATIF)

> **PANDUAN METODOLOGI:**  
> - Skala 5-poin Likert (`1` = Sangat Tidak Setuju s.d. `5` = Sangat Setuju).
> - Seluruh 5 butir berstatus **WAJIB DIISI (Required)**.
> - Butir-butir ini **BUKAN** skala psikometrik terpadu dan **TIDAK AKAN** dijumlahkan menjadi skor komposit/indeks. Setiap butir dianalisis secara terpisah.

| Kode Butir | Aspek yang Diukur | Teks Pernyataan (Bahasa Indonesia Baku) | Skala Pilihan |
| :---: | :--- | :--- | :---: |
| **CLAR_01** | Kejelasan Sinyal Skrining vs Diagnosis | Perbedaan antara sinyal skrining non-laboratorium dan diagnosis medis formal disajikan dengan jelas. | 1 – 2 – 3 – 4 – 5 |
| **CLAR_02** | Kejelasan Arah Faktor XAI | Penjelasan "Why this result?" memperjelas faktor-faktor input mana yang meningkatkan atau menurunkan skor skrining. | 1 – 2 – 3 – 4 – 5 |
| **CLAR_03** | Pembedaan Rekomendasi AI vs Keputusan Manusia | Antarmuka secara jelas membedakan rekomendasi awal mesin dari keputusan rujukan akhir oleh manusia. | 1 – 2 – 3 – 4 – 5 |
| **CLAR_04** | Kendali Peninjauan & Pengesampingan | Saya merasa memegang kendali ketika meninjau atau mengesampingkan (*override*) rekomendasi rujukan mesin. | 1 – 2 – 3 – 4 – 5 |
| **CLAR_05** | Kejelasan Makna Lab Tahap-2 | Hasil HbA1c Tahap-2 secara jelas menunjukkan rentang acuan laboratorium dan bukan diagnosis klinis otomatis. | 1 – 2 – 3 – 4 – 5 |

---

## SEKSI 5: UMPAN BALIK KUALITATIF TERBUKA (3 BUTIR)

> **STATUS KEWAJIBAN PENGISIAN (SUPERVISOR DECISION REQUIRED):**  
> Protokol E1 menetapkan teks ketiga pertanyaan ini, namun tidak secara eksplisit mengunci apakah kolom isian bebas ini berstatus wajib diisi (*mandatory*) atau opsional (*optional*). Rekomendasi operasional: **Opsional dengan anjuran pengisian**, agar peserta tidak terhalang mengirim kuesioner jika tidak memiliki komentar khusus. Keputusan final diserahkan kepada Pembimbing/Komite Etik.

### Butir 1 (`QUAL_01` - Hambatan Alur Kerja Skrining)
- **Tipe Pertanyaan:** Paragraf Bebas (*Long Text Area*)
- **Status:** *SUPERVISOR DECISION REQUIRED* (Default rekomendasi: Opsional)
- **Teks Pertanyaan:**  
  *"Bagian mana dari alur kerja skrining dan peninjauan yang paling membingungkan atau sulit untuk dinavigasi?"*

### Butir 2 (`QUAL_02` - Saran Penyempurnaan Grafik XAI)
- **Tipe Pertanyaan:** Paragraf Bebas (*Long Text Area*)
- **Status:** *SUPERVISOR DECISION REQUIRED* (Default rekomendasi: Opsional)
- **Teks Pertanyaan:**  
  *"Apa hal yang dapat diubah untuk membuat penjelasan faktor 'Why this result?' lebih mudah dipahami?"*

### Butir 3 (`QUAL_03` - Kejelasan Batas Tanggung Jawab Keputusan)
- **Tipe Pertanyaan:** Paragraf Bebas (*Long Text Area*)
- **Status:** *SUPERVISOR DECISION REQUIRED* (Default rekomendasi: Opsional)
- **Teks Pertanyaan:**  
  *"Apakah Anda mengalami momen di mana Anda tidak yakin apakah komputer atau manusia yang bertanggung jawab atas suatu keputusan? Jika ya, mohon jelaskan."*
