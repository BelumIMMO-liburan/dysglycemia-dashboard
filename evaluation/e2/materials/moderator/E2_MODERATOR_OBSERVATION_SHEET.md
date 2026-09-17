# Lembar Observasi Moderator (Moderator Observation Sheet)
## Evaluasi Prototipe Antarmuka Skrining Risiko Disglikemia Dua Tahap

**Kode Dokumen:** `E2-MOD-OBS-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tingkat Kerahasiaan:** **PENELITI / MODERATOR SAJA**  

---

### Data Administrasi Sesi
- **Kode Peserta:** `____________________` *(Wajib diisi, mis. `PILOT001` atau `P001`)*
- **Tanggal Sesi:** `_____ / _____ / 2026`
- **Nama / Inisial Moderator:** `____________________`
- **Lingkungan Perangkat:** [ ] Desktop (Monitor Resolusi: `_____________`) | [ ] Laptop (Ukuran Layar: `_______`)
- **Peramban Web (*Browser*):** [ ] Google Chrome | [ ] Mozilla Firefox | [ ] Microsoft Edge
- **Waktu Mulai Sesi:** `____ : ____` WIB | **Waktu Selesai Sesi:** `____ : ____` WIB

---

### Rubrik Tingkat Bantuan (*Assistance Level*)
- **Tingkat 0 (Mandiri):** Peserta menyelesaikan tugas tanpa intervensi verbal/fisik dari moderator.
- **Tingkat 1 (Klarifikasi Pertanyaan):** Moderator mengulang instruksi tugas tanpa memberi petunjuk langkah solusi.
- **Tingkat 2 (Pengarahan Langkah):** Moderator mengarahkan perhatian peserta ke elemen antarmuka tertentu.
- **Tingkat 3 (Demonstrasi / Pengambilalihan):** Moderator menunjukkan langsung tindakan yang harus dilakukan.

### Taksonomi Kode Kesalahan (*Error Codes*)
- `NAV_ERR`: Kesalahan navigasi menu/tautan atau tersesat di halaman.
- `INPUT_ERR`: Salah mengetik angka, format desimal, atau salah memilih opsi radio.
- `INTERP_ERR`: Salah membaca rekomendasi AI, arah kontribusi, atau rentang lab.
- `WORKFLOW_ERR`: Melewatkan tahapan wajib (mis. lupa klik *Review Inputs* atau *Confirm*).
- `SYS_ERR`: Kendala teknis peramban web atau kelambatan respon sistem.

---

### Matriks Observasi Kinerja Tugas (Tugas 1 s.d. 6)

#### TUGAS 1: Penginputan Data Skrining Awal (Case Alpha)
- **Kriteria Berhasil:** Ketujuh parameter dimasukkan sesuai kartu, ringkasan diperiksa, tombol *Run Screening* ditekan hingga halaman hasil terbuka.
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal / Bantuan Penuh (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `NAV_ERR` | [ ] `INPUT_ERR` | [ ] `WORKFLOW_ERR` | [ ] `SYS_ERR`
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator (Objektif / Non-Identifikasi):** `___________________________________________________`

---

#### TUGAS 2: Pemeriksaan Hasil dan Penjelasan XAI (Case Alpha)
- **Kriteria Berhasil:** Membuka grafik 7 faktor, menyebutkan faktor usia (*Age*) sebagai pendorong tertinggi, dan menyebutkan minimal 1 faktor penahan yang valid (*Sedentary Time*, *Waist*, *Non-smoker*, atau *Male*).
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal / Salah Interpretasi (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `NAV_ERR` | [ ] `INTERP_ERR` | [ ] `SYS_ERR`
- **Faktor Positif yang Disebutkan:** [ ] Age (+0.418) [BENAR] | [ ] Lainnya: `_________________`
- **Faktor Negatif yang Disebutkan:** [ ] Sedentary (-0.473) | [ ] Waist (-0.160) | [ ] Non-smoker (-0.118) | [ ] Male (-0.027) | [ ] Lainnya: `______`
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator:** `___________________________________________________`

---

#### TUGAS 3: Peninjauan Keputusan Manusia - Penerimaan Rekomendasi (Case Alpha)
- **Kriteria Berhasil:** Mengisi kode peninjau dengan kode peserta dan menekan tombol *Accept Recommendation* hingga status berubah menjadi *Accepted: Referral Recommended*.
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `INPUT_ERR` (Kode salah) | [ ] `WORKFLOW_ERR` | [ ] `SYS_ERR`
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator:** `___________________________________________________`

---

#### TUGAS 4: Alur Pengesampingan Keputusan Manusia - Override (Case Beta)
- **Kriteria Berhasil:** Memasukkan Case Beta, membuka modal override, mengisi kode peninjau, memilih alasan terstruktur *"Referral is preferred as a precaution"*, mengisi catatan skenario, dan menyimpan konfirmasi override.
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `NAV_ERR` | [ ] `INPUT_ERR` | [ ] `WORKFLOW_ERR` | [ ] `SYS_ERR`
- **Alasan Terstruktur Sesuai:** [ ] Ya | [ ] Tidak (`__________________`)
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator:** `___________________________________________________`

---

#### TUGAS 5: Penilaian Laboratorium Tahap-2 HbA1c (Case Alpha)
- **Kriteria Berhasil:** Membuka kembali Case Alpha yang berstatus rujukan, menekan *Proceed to Stage-2*, mengisi nilai HbA1c 6.1%, mengonfirmasi hingga hasil rentang prediabetes muncul.
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `NAV_ERR` | [ ] `INPUT_ERR` | [ ] `INTERP_ERR` | [ ] `SYS_ERR`
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator:** `___________________________________________________`

---

#### TUGAS 6: Pemeriksaan Transparansi Jejak Audit Riwayat Kasus (Case Beta)
- **Kriteria Berhasil:** Membuka menu *History*, memilih *View Case* pada Case Beta, mengidentifikasi bahwa rekomendasi awal mesin tetap tercatat, serta mengonfirmasi status Tahap-2 berstatus *Pending Stage-2 Assessment*.
- **Hasil Tugas:** [ ] Berhasil (1) | [ ] Gagal (0)
- **Tingkat Bantuan Tertinggi:** [ ] 0 (Mandiri) | [ ] 1 (Klarifikasi) | [ ] 2 (Pengarahan) | [ ] 3 (Demonstrasi)
- **Kode Kesalahan Teramati:** [ ] Tidak Ada | [ ] `NAV_ERR` | [ ] `INTERP_ERR` | [ ] `SYS_ERR`
- **Verifikasi Keterlacakan Mesin:** [ ] Berhasil Menemukan Rekomendasi Awal Mesin | [ ] Gagal
- **Durasi Tugas (Opsional):** Mulai: `____:____` | Selesai: `____:____` (Detik: `_______`)
- **Catatan Moderator:** `___________________________________________________`

---

### Verifikasi Pasca-Tugas & Transisi Kuesioner
- [ ] Peserta telah menyelesaikan seluruh 6 tugas antarmuka.
- [ ] Peserta telah diarahkan menuju kuesioner digital eksternal tertutup (*closed-book*).
- [ ] Moderator memastikan peserta tidak membuka kembali antarmuka selama pengisian kuesioner pemahaman.
- [ ] Kode Peserta pada kuesioner terverifikasi identik dengan lembar ini.
