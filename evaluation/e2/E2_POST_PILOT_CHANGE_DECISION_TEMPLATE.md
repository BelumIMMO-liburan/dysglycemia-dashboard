# Template Keputusan Perubahan Pasca-Pilot (Post-Pilot Change Decision Template)
## Kerangka Kerja Tata Kelola Evaluasi untuk Menanggapi Temuan Sesi Kelayakan ($N=3\text{--}5$)

**Kode Dokumen:** `E2-CHANGE-DECISION-TEMPLATE-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Tujuan Dokumen:**  
Menetapkan mekanisme tata kelola formal untuk mengevaluasi, mengklasifikasikan, dan memutuskan tindak lanjut terhadap setiap anomali, friksi usability, atau ketidakjelasan instrumen yang teridentifikasi selama sesi pilot, tanpa melanggar prinsip kebekuan perangkat lunak penelitian.

---

### 1. Taksonomi Klasifikasi Keputusan Perubahan

Setiap temuan atau insiden dari sesi pilot wajib diklasifikasikan ke dalam salah satu dari 6 kategori berikut:

```
+------------------------------------+-----------------------------------------------------+
| Kategori Klasifikasi               | Dampak & Ruang Lingkup Tindak Lanjut                 |
+------------------------------------+-----------------------------------------------------+
| 1. NO CHANGE                       | Dinilai sebagai variasi wajar perilaku pengguna.   |
| 2. DOCUMENTATION CLARIFICATION     | Penyesuaian redaksional panduan moderator/runbook.  |
| 3. INSTRUMENT WORDING CHANGE       | Perbaikan redaksi kuesioner pemahaman/persepsi.    |
| 4. TASK CHANGE                     | Penyesuaian urutan instruksi kartu skenario.       |
| 5. SOFTWARE DEFECT                 | Ditemukan galat/bug teknis pada kode prototipe.   |
| 6. PROTOCOL CHANGE                 | Perubahan metodologis besar pada desain studi.     |
+------------------------------------+-----------------------------------------------------+
```

---

### 2. Prinsip Kebekuan Perangkat Lunak (*Software Freeze Invariant*)
> **ATURAN MUTLAK RISET:**  
> Apabila temuan pilot diklasifikasikan sebagai **SOFTWARE DEFECT** atau memerlukan modifikasi antarmuka/model:
> 1. Perangkat lunak `research-prototype-v1.0` **DILARANG DIUBAH SECARA DIAM-DIAM**.
> 2. Diperlukan rilis versi formal baru (misalnya: `research-prototype-v1.1`), disertai catatan perubahan (*changelog*) dan re-verifikasi 144 unit test serta hash artefak.
> 3. Protokol evaluasi E1 wajib ditingkatkan versinya (misalnya menjadi `v1.1.0`) dengan justifikasi tertulis dan persetujuan dosen pembimbing.
> 4. Data pilot yang telah dikumpulkan sebelum perbaikan perangkat lunak **TIDAK BOLEH DIGABUNGKAN** ke dalam studi formal.

---

### 3. Formulir Log Keputusan Perubahan (Template Pencatatan)

Gunakan tabel di bawah ini untuk mencatat setiap temuan pasca-pilot:

| ID Temuan | Deskripsi Temuan / Kendala | Bukti Insiden / Observasi | Klasifikasi Keputusan | Rencana Tindak Lanjut | Dampak terhadap Protokol / Rilis | Status Tindak Lanjut |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: |
| `PILOT-F01` | *Contoh: Peserta bingung mencari tombol Show all 7 factors* | Lembar observasi PILOT001 & PILOT002 (Assistance Level 1) | `DOCUMENTATION CLARIFICATION` | Tambahkan penekanan visual pada teks orientasi moderator Tahap 6 | Tidak berdampak pada perangkat lunak / protokol | `DRAFT / PENDING` |
| `PILOT-F02` | *Contoh: Teks butir kuesioner membingungkan* | Catatan kualitatif PILOT003 | `INSTRUMENT WORDING CHANGE` | Revisi frasa bahasa Indonesia pada cetak biru instrumen | Memerlukan persetujuan pembimbing | `DRAFT / PENDING` |
| `PILOT-F03` | *Contoh: Tombol konfirmasi tidak merespon pada resolusi tertentu* | Log insiden INC-001 | `SOFTWARE DEFECT` | Investigasi bug CSS/JS, siapkan rilis v1.0.1 jika disetujui | Membatalkan rilis v1.0, memerlukan protokol baru | `DRAFT / PENDING` |

---

### 4. Prosedur Pengesahan Keputusan
1. **Analisis Triase:** Peneliti utama mendokumentasikan seluruh temuan dan mengusulkan klasifikasi.
2. **Tinjauan Pembimbing:** Laporan triase diajukan kepada Dosen Pembimbing untuk disetujui.
3. **Keputusan Status Data Pilot:** Menentukan apakah data pilot dapat digunakan sebagai bukti kelayakan operasional (*feasibility proof*) atau apakah pilot perlu diulang setelah tindakan perbaikan selesai.
