# Buku Panduan Tugas Peserta (Task Booklet)
## Skenario Tugas Terstruktur Evaluasi Antarmuka Skrining Dua Tahap

**Kode Dokumen:** `E2-TASK-BOOKLET-ID-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Bahasa Pengantar:** Bahasa Indonesia  
**Petunjuk Umum:**  
- Buku panduan ini berisi instruksi pengerjaan 6 tugas interaksi mandiri menggunakan prototipe antarmuka skrining.
- Kerjakan setiap tugas secara berurutan mulai dari Tugas 1 hingga Tugas 6.
- Gunakan data profil yang tertera pada Kartu Kasus yang diberikan oleh moderator.
- Setelah menyelesaikan seluruh tugas, Anda akan dipandu untuk mengisi kuesioner evaluasi akhir.

---

### TUGAS 1: Penginputan Data Skrining Awal Non-Laboratorium
- **Profil Kasus Acuan:** `CASE-ALPHA` (Lihat Kartu Kasus Alpha)
- **Tujuan Interaksi:** Memasukkan parameter skrining awal ke dalam sistem dan menjalankan perhitungan skrining.
- **Langkah Pengerjaan:**
  1. Pada menu navigasi sebelah kiri (*sidebar*), klik menu **New Screening**.
  2. Masukkan ketujuh nilai parameter kesehatan yang tertera pada **Kartu Kasus Alpha** ke dalam formulir input.
  3. Klik tombol **Review Inputs** untuk memeriksa ringkasan data yang telah Anda masukkan.
  4. Periksa kembali kecocokan nilai pada kartu ringkasan. Jika sudah sesuai, klik tombol **Run Screening** untuk memproses data skrining.
- **Penyelesaian:** Halaman akan berpindah ke tampilan hasil skrining kasus (*Screening Result*).

---

### TUGAS 2: Pemeriksaan Hasil Skrining dan Penjelasan Faktor Model
- **Profil Kasus Acuan:** `CASE-ALPHA` (Melanjutkan hasil dari Tugas 1)
- **Tujuan Interaksi:** Meninjau sinyal skrining, rekomendasi awal sistem, dan grafik penjelasan kontribusi faktor (*explainable AI*).
- **Langkah Pengerjaan:**
  1. Perhatikan kartu utama hasil skrining di bagian atas halaman:
     - Amati lencana sinyal skrining (*Screening Signal*).
     - Amati rekomendasi rujukan awal yang dihasilkan sistem (*AI Referral Recommendation*).
  2. Gulir ke bawah menuju bagian kartu **Why this result?**.
  3. Klik tombol **Show all 7 factors** untuk membuka tampilan lengkap grafik kontribusi ketujuh faktor input.
  4. Amati arah batang dan nilai kontribusi masing-masing faktor:
     - Perhatikan faktor-faktor yang berada di bawah label *Pushes screening score higher* (faktor yang mendorong skor lebih tinggi).
     - Perhatikan faktor-faktor yang berada di bawah label *Pushes screening score lower* (faktor yang menahan skor lebih rendah).
  5. Sampaikan secara lisan kepada moderator faktor mana yang paling mendorong skor menjadi lebih tinggi dan sebutkan minimal satu faktor yang menahan skor lebih rendah.
- **Penyelesaian:** Konfirmasi pengamatan kepada moderator sebelum beralih ke tugas berikutnya.

---

### TUGAS 3: Peninjauan Keputusan oleh Manusia (Penerimaan Rekomendasi)
- **Profil Kasus Acuan:** `CASE-ALPHA` (Melanjutkan hasil dari Tugas 2)
- **Tujuan Interaksi:** Menyelesaikan alur peninjauan manusia (*Human Guided Review*) dengan menyetujui rekomendasi sistem.
- **Langkah Pengerjaan:**
  1. Pada halaman hasil Case Alpha, gulir ke bagian paling bawah menuju panel kerja **Human Review**.
  2. Sesuai skenario penelitian untuk kasus ini, instruksi meminta Anda untuk **menyetujui rekomendasi sistem (Accept Recommendation)**.
  3. Masukkan **Kode Peserta** Anda (misalnya: `PILOT001` atau kode yang tercantum pada lembar Anda) ke dalam kolom isian **Reviewer Code**.
  4. Klik tombol **Accept Recommendation** untuk mengonfirmasi dan menyimpan keputusan akhir peninjauan Anda.
- **Penyelesaian:** Perhatikan pembaruan status pada antarmuka yang menunjukkan keputusan telah tersimpan.

---

### TUGAS 4: Alur Pengesampingan Keputusan oleh Manusia (Human Override)
- **Profil Kasus Acuan:** `CASE-BETA` (Lihat Kartu Kasus Beta dan Kartu Skenario Override)
- **Tujuan Interaksi:** Melakukan penginputan kasus baru dan mempraktikkan alur pengesampingan keputusan (*override*) dari rekomendasi awal sistem.
- **Langkah Pengerjaan:**
  1. Klik menu **New Screening** pada navigasi kiri untuk memulai skrining baru.
  2. Masukkan ketujuh nilai parameter yang tertera pada **Kartu Kasus Beta**.
  3. Klik **Review Inputs**, periksa ringkasan, lalu klik **Run Screening**.
  4. Perhatikan hasil skrining awal untuk Case Beta (amati sinyal dan rekomendasi awal sistem).
  5. Sesuai skenario simulasi penelitian pada **Kartu Skenario Override Beta**, instruksi meminta Anda untuk **mengesampingkan rekomendasi awal sistem** menjadi rujukan (*Refer*).
  6. Pada panel kerja **Human Review**, klik tombol **Override Recommendation** untuk membuka jendela dialog pengesampingan.
  7. Periksa ringkasan perubahan keputusan yang ditampilkan di dalam dialog.
  8. Masukkan **Kode Peserta** Anda ke dalam kolom **Reviewer Code**.
  9. Pilih alasan terstruktur persis sesuai instruksi kartu skenario:  
     **"Referral is preferred as a precaution"**
  10. Ketikkan catatan skenario persis sesuai kartu instruksi:  
      **"Individual reports unrecorded family history of early diabetes"**
  11. Klik tombol **Confirm Override** untuk menyimpan pengesampingan keputusan tersebut.
- **Penyelesaian:** Amati bahwa status peninjauan diperbarui dan rekomendasi awal sistem tetap dapat ditelusuri pada riwayat.

---

### TUGAS 5: Penilaian Lanjutan Laboratorium HbA1c Tahap-2
- **Profil Kasus Acuan:** `CASE-ALPHA` (PENTING: Gunakan kembali Case Alpha)
- **Tujuan Interaksi:** Menjalankan alur pencatatan pemeriksaan laboratorium lanjutan untuk kasus yang berstatus rujukan.
- **Langkah Pengerjaan:**
  1. Buka kembali halaman hasil **Case Alpha** (dapat menggunakan tombol kembali pada peramban web atau melalui tautan kasus).
  2. Karena Case Alpha memiliki keputusan akhir rujukan (*Refer*), temukan dan klik tombol **Proceed to Stage-2 HbA1c Assessment**.
  3. Pada formulir pemeriksaan laboratorium Tahap-2, masukkan nilai HbA1c dari **Kartu Kasus Alpha Tahap-2**, yaitu: **6.1%**.
  4. Klik tombol **Review HbA1c Value** untuk meninjau nilai yang dimasukkan.
  5. Klik tombol **Confirm Laboratory Result** untuk menyimpan hasil laboratorium.
  6. Amati rentang acuan laboratorium yang ditampilkan oleh sistem beserta pemberitahuan terkait batasannya.
- **Penyelesaian:** Hasil pemeriksaan Tahap-2 tersimpan dan ringkasan kasus menunjukkan status tahapan telah lengkap.

---

### TUGAS 6: Pemeriksaan Jejak Audit dan Riwayat Kasus (Audit Trail)
- **Profil Kasus Acuan:** `CASE-BETA` (Pemeriksaan pada tabel Riwayat)
- **Tujuan Interaksi:** Meninjau transparansi riwayat audit, memverifikasi keterlacakan rekomendasi awal mesin, keputusan manusia, dan status tahapan kasus.
- **Langkah Pengerjaan:**
  1. Pada navigasi sebelah kiri, klik menu **History**.
  2. Pada tabel riwayat skrining, temukan baris catatan untuk **Case Beta** (perhatikan label status peninjauannya).
  3. Pada kolom tindakan (*Action*), klik tombol **View Case**.
  4. Pada halaman rincian riwayat kasus, telusuri kronologi tiga bagian yang tersedia:
     - **Bagian 1 (Data Tahap-1 & Rekomendasi Awal Mesin):** Periksa apakah rekomendasi awal mesin masih tercatat dan dapat dilihat.
     - **Bagian 2 (Keputusan Peninjauan Manusia):** Periksa catatan keputusan akhir manusia, kode peninjau, alasan terstruktur, serta catatan pengesampingan.
     - **Bagian 3 (Status Tahap-2):** Periksa status tahapan laboratorium lanjutan untuk Case Beta.
- **Penyelesaian:** Sampaikan kepada moderator hasil konfirmasi Anda terkait keterlacakan rekomendasi awal mesin dan status tahapan kasus.
