# Kunci Status Sistem & Rubrik Jawaban Moderator (Master Answer Key)
## Evaluasi Prototipe Antarmuka Skrining Dua Tahap

**Kode Dokumen:** `E2-MOD-KEY-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tingkat Kerahasiaan:** **PENELITI / MODERATOR SAJA — DILARANG DIBERIKAN / DILIHAT PESERTA**  
*(RESEARCHER / MODERATOR ONLY — DO NOT SHOW OR DISTRIBUTE TO PARTICIPANTS)*

---

### 1. Tujuan Dokumen
Dokumen ini memuat nilai acuan mutlak hasil keluaran sistem beku (*frozen runtime outputs*), bobot kontribusi model statistik (*GAM contributions*), klasifikasi laboratorium Tahap-2, serta kriteria objektif keberhasilan tugas untuk memandu pencatatan observasi oleh moderator selama sesi evaluasi.

---

### 2. Status Keluaran Sistem untuk Case Alpha (Kasus 1, 2, 3, dan 5)

#### 2.1 Parameter Input (Canonical Seven)
- Usia: `56` tahun | Jenis Kelamin: `Male` | BMI: `31.2` kg/m²
- Hipertensi: `Yes` | Riwayat Merokok: `No` | Lingkar Pinggang: `102.0` cm | Waktu Sedentari: `480` menit/hari

#### 2.2 Hasil Inferensi Model Beku (D2.3)
- **Probabilitas Skrining Terhitung:** `0.272969` (dibulatkan pada tampilan: **27.30%**)
- **Ambang Batas Keputusan:** `0.1389` (13.89%)
- **Sinyal Skrining:** **Elevated Screening Signal** (Lencana Merah / Coral)
- **Rekomendasi Rujukan AI:** **Refer**

#### 2.3 Kontribusi Fitur Model GAM (D2.5 - Penjelasan "Why this result?")
| Nama Fitur | Nilai Input | Kontribusi Log-Odds | Arah Pengaruh | Peringkat pada Tampilan |
| :--- | :--- | :---: | :---: | :--- |
| **Age (Usia)** | 56 th | `+0.417980` (dibulatkan: `+0.418`) | **Pushes Higher** | **Faktor Positif Teratas (#1 Pendorong)** |
| **Hypertension (Hipertensi)** | Yes | `+0.103343` (dibulatkan: `+0.103`) | **Pushes Higher** | Faktor Pendorong (#2) |
| **BMI** | 31.2 kg/m² | `+0.004917` (dibulatkan: `+0.005`) | **Pushes Higher** | Faktor Pendorong (#3) |
| **Biological Sex** | Male | `-0.026593` (dibulatkan: `-0.027`) | **Pushes Lower** | Faktor Penahan / Penurun (#4) |
| **Smoking History** | Non-smoker | `-0.117616` (dibulatkan: `-0.118`) | **Pushes Lower** | Faktor Penahan / Penurun (#3) |
| **Waist Circumference** | 102.0 cm | `-0.159560` (dibulatkan: `-0.160`) | **Pushes Lower** | Faktor Penahan / Penurun (#2) |
| **Sedentary Time** | 480 mnt/hari | `-0.472934` (dibulatkan: `-0.473`) | **Pushes Lower** | **Faktor Penahan / Penurun Terbesar (#1)** |

> **Rubrik Observasi Tugas 2:**  
> - *Faktor pendorong tertinggi yang benar:* **Usia (Age)** (`+0.418`).  
> - *Faktor penahan/penurun yang valid (cukup sebutkan salah satu):* **Sedentary Time** (`-0.473`), **Waist Circumference** (`-0.160`), **Smoking: Non-smoker** (`-0.118`), atau **Sex: Male** (`-0.027`).

#### 2.4 Hasil Peninjauan Manusia (Tugas 3)
- **Keputusan Peninjau:** `Accept Recommendation`
- **Kode Peninjau yang Tersimpan:** Sesuai Kode Peserta (mis. `PILOT001`)
- **Status Akhir Kasus:** `Accepted: Referral Recommended`

#### 2.5 Hasil Penilaian Laboratorium Tahap-2 (Tugas 5)
- **Nilai Input HbA1c:** `6.1%`
- **Klasifikasi Rentang Laboratorium:** **Prediabetes range (5.7% – 6.4%)**
- **Status Kasus:** `completed_stage2`

---

### 3. Status Keluaran Sistem untuk Case Beta (Kasus 4 dan 6)

#### 3.1 Parameter Input (Canonical Seven)
- Usia: `32` tahun | Jenis Kelamin: `Female` | BMI: `23.5` kg/m²
- Hipertensi: `No` | Riwayat Merokok: `Yes` | Lingkar Pinggang: `74.0` cm | Waktu Sedentari: `300` menit/hari

#### 3.2 Hasil Inferensi Model Beku (D2.3)
- **Probabilitas Skrining Terhitung:** `0.054663` (dibulatkan pada tampilan: **5.47%**)
- **Ambang Batas Keputusan:** `0.1389` (13.89%)
- **Sinyal Skrining:** **Lower Screening Signal** (Lencana Abu-abu Netral)
- **Rekomendasi Rujukan AI:** **No Referral**

#### 3.3 Hasil Pengesampingan Keputusan oleh Manusia (Tugas 4)
- **Aksi:** `Override Recommendation` (dari `No Referral` menjadi `Refer`)
- **Kode Peninjau:** Sesuai Kode Peserta (mis. `PILOT001`)
- **Alasan Terstruktur Wajib:** `Referral is preferred as a precaution` (kode internal: `precautionary_referral`)
- **Catatan Skenario Wajib:** `"Individual reports unrecorded family history of early diabetes"`
- **Status Akhir Kasus:** `Overridden to Refer`

#### 3.4 Status Audit dan Keterlacakan Riwayat (Tugas 6)
- **Tampilan Riwayat:** Baris Case Beta menampilkan lencana `Overridden to Refer`.
- **Rincian Kasus (View Case):**
  - *Rekomendasi Awal Mesin:* Tetap tercatat sebagai `No Referral` ($p \approx 5.5\%$).
  - *Keputusan Manusia:* `Overridden to Refer`, mencantumkan kode peserta, alasan terstruktur, dan catatan skenario secara utuh.
  - *Status Tahap-2:* `Pending Stage-2 Assessment` (karena tidak dilanjutkan ke Tahap-2 pada skenario protokol).

---

### 4. Kunci Jawaban Resmi Kuesioner Pemahaman Objektif (8 Butir)
*(Hanya untuk evaluasi pasca-sesi oleh peneliti; dilarang dibagikan kepada peserta)*

| Butir | Kode Domain | Kunci Benar | Ringkasan Konsep Jawaban |
| :---: | :---: | :---: | :--- |
| **COMP_01** | Domain A | **[B]** | Estimasi probabilitas di atas ambang batas, merekomendasikan lab HbA1c Tahap-2. |
| **COMP_02** | Domain B | **[B]** | Probabilitas di bawah ambang keputusan, rujukan lab lanjutan tidak direkomendasikan saat ini. |
| **COMP_03** | Domain C | **[A]** | Faktor input secara matematis meningkatkan skor skrining dalam perhitungan aditif. |
| **COMP_04** | Domain D | **[C]** | Grafik menampilkan asosiasi statistik & kontribusi aditif, bukan bukti sebab-akibat klinis. |
| **COMP_05** | Domain E | **[B]** | Keputusan rujukan manusia diperbarui, kalkulasi awal AI tetap tersimpan dalam jejak audit. |
| **COMP_06** | Domain F | **[B]** | Menampilkan kategorisasi rentang lab HbA1c berdasarkan kriteria acuan standar (ADA), perlu interpretasi klinis. |
| **COMP_07** | Domain G | **[C]** | Rekomendasi awal mesin tetap tercatat permanen dalam jejak audit bersama alasan dan kode peninjau. |
| **COMP_08** | Domain H | **[B]** | Peninjau manusia menyetujui rekomendasi rujukan AI pada 85% kasus yang ditinjau. |

---

### 5. Rekapitulasi Cardinality Basis Data Per Sesi Selesai
Setelah satu sesi peserta selesai sempurna, basis data sesi (`db_study.sqlite3`) harus memiliki:
- `ScreeningRecord` = **2** (Case Alpha dan Case Beta)
- `ScreeningExplanation` = **2** (Penjelasan faktor Alpha dan Beta)
- `HumanReview` = **2** (Alpha: `accepted` / `refer`; Beta: `overridden` / `refer`)
- `Stage2Assessment` = **1** (Hanya Case Alpha, nilai 6.1%, `prediabetes_range`)
