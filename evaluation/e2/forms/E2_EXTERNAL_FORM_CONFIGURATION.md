# Konfigurasi Privasi dan Pengaturan Platform Formulir Eksternal
## Panduan Teknis Pengaturan Formulir Evaluasi Bebas-PII (Privacy & Governance Configuration)

**Kode Dokumen:** `E2-FORM-CONFIG-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tujuan Dokumen:**  
Menjamin bahwa platform survei digital eksternal mana pun yang dipilih (Google Forms, Microsoft Forms, Qualtrics, dsb.) dikonfigurasikan dengan setelan privasi maksimal sehingga tidak mengumpulkan identitas personal (*Personally Identifiable Information / PII*) peserta secara diam-diam.

---

### 1. Prinsip Utama Tata Kelola Privasi Formulir
1. **Anonimitas Akun Pengguna:** Pengisian formulir tidak boleh mewajibkan *login* akun institusi atau email pribadi yang dapat merekam identitas pengirim secara otomatis.
2. **Kunci Penaut Tunggal:** Identitas responden hanya diwakili oleh **Kode Peserta** (*Participant Code*, mis. `PILOT001`) yang diinput manual pada Butir 1.1.
3. **Pencegahan Kebocoran Jawaban:** Kuis pemahaman objektif harus berfungsi murni sebagai instrumen perekam data, **BUKAN** sebagai kuis interaktif dengan nilai atau kunci jawaban terbuka.

---

### 2. Matriks Pengaturan Wajib Per Fitur

| Fitur Platform | Pengaturan Wajib | Justifikasi Metodologis & Tata Kelola |
| :--- | :---: | :--- |
| **Kumpulkan Alamat Email (*Collect Email*)** | **NONAKTIF (OFF / DO NOT COLLECT)** | Menghindari perekaman PII secara langsung ke dalam dataset analitis. |
| **Wajibkan Masuk Akun (*Require Sign-in*)** | **NONAKTIF (OFF / ANYONE WITH LINK)** | Memungkinkan pengisian tanpa menautkan akun Google/Microsoft peserta. |
| **Batasi 1 Tanggapan (*Limit to 1 Response*)** | **NONAKTIF (OFF)\*** | Pada Google Forms, fitur ini secara otomatis memaksa responden login akun Google. Pengendalian duplikasi dilakukan secara operasional melalui *Participant Code Check*. |
| **Tampilkan Ringkasan Hasil Publik (*Show Summary Charts*)** | **NONAKTIF (OFF)** | Mencegah peserta melihat distribusi tanggapan peserta lain. |
| **Tampilkan Nilai Kuis Langsung (*Immediate Quiz Score*)** | **NONAKTIF (OFF)** | Kuis pemahaman dinilai secara *offline* oleh peneliti; peserta tidak boleh mengetahui skor atau kunci jawaban. |
| **Tampilkan Kunci Jawaban Benar (*Show Correct Answers*)** | **NONAKTIF (OFF)** | Menjaga kerahasiaan bank soal pemahaman agar tidak bocor antarpeserta. |
| **Acak Urutan Pertanyaan (*Shuffle Question Order*)** | **NONAKTIF (OFF)** | Urutan instrumen harus terstandarisasi untuk seluruh peserta (Seksi 1 $\to$ 2 $\to$ 3 $\to$ 4 $\to$ 5). |
| **Pesan Konfirmasi Pengiriman (*Confirmation Message*)** | **TEKS BAKU TERKUNCI** | Tampilkan: *"Terima kasih. Respons evaluasi Anda telah berhasil direkam. Silakan konfirmasikan kepada moderator bahwa pengisian telah selesai."* |

*\*Catatan Khusus Fitur "Limit to 1 response":*  
Jika platform Qualtrics atau survei lokal institusi memiliki mekanisme pencegahan duplikasi berbasis *cookie* tanpa mencatat identitas login/email, fitur tersebut boleh diaktifkan. Namun pada platform publik seperti Google Forms, fitur ini **WAJIB MATI** agar privasi akun terlindungi.

---

### 3. Checklist Verifikasi Sebelum Administrasi Sesi

Sebelum tautan kuesioner diserahkan kepada peserta mana pun:
- [ ] Pengaturan pengumpulan email diverifikasi dalam posisi MATI (*Do not collect*).
- [ ] Formulir diuji menggunakan mode penyamaran (*Incognito/Private Browsing*) dan dipastikan dapat diakses tanpa meminta login akun.
- [ ] Kolom pertama adalah *Participant Code* dengan status wajib diisi.
- [ ] Seluruh butir kuis pemahaman (8 butir), SUS (10 butir), dan kejelasan (5 butir) berstatus *Required*.
- [ ] Mode kuis interaktif (*Make this a quiz*) dimatikan, atau jika aktif, opsi *Release grades immediately* dan *Show correct answers* dinonaktifkan.
- [ ] Formulir diuji coba kirim 1 kali (*dry run*) untuk memverifikasi struktur kolom berkas hasil ekspor (*CSV / XLSX*).
