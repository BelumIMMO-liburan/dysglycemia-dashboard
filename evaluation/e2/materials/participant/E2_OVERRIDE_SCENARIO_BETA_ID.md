# Kartu Instruksi Skenario Pengesampingan (Human Override): Case Beta
## Panduan Tugas Interaksi Peninjauan Keputusan (Tugas 4)

**Kode Skenario:** `OVERRIDE-SCENARIO-BETA`  
**Kasus Terkait:** `CASE-BETA`  
**Peruntukan:** Materi Peserta (Tugas 4)  

---

### Konteks Skenario Simulasi Penelitian
> **PEMBERITAHUAN PENTING:**  
> Skenario ini adalah **simulasi instruksi terstruktur** untuk menguji apakah antarmuka memungkinkan pengguna melakukan pengesampingan keputusan (*human override*) dengan lancar. Anda **TIDAK DIMINTA** untuk membuat keputusan klinis mandiri atau mendiagnosis kondisi medis. Ikuti langkah terstruktur di bawah ini secara persis.

---

### Instruksi Pengesampingan Terstruktur

Pada kasus **Case Beta**, sistem menghasilkan rekomendasi awal **No Referral** (Tidak Perlu Rujukan).  
Skenario protokol penelitian menginstruksikan Anda untuk **mengesampingkan rekomendasi awal mesin menjadi rujukan (REFER)** berdasarkan informasi kontekstual simulasi berikut:

1. **Arah Perubahan Keputusan:**
   - Dari: `No Referral` (Rekomendasi Mesin)
   - Menjadi: `Refer` (Keputusan Akhir Manusia)

2. **Langkah pada Antarmuka:**
   - Klik tombol **Override Recommendation** pada panel Human Review.
   - Masukkan **Kode Peserta** Anda pada kolom `Reviewer Code`.

3. **Pilihan Alasan Terstruktur (Structured Reason):**  
   Pilih opsi alasan dropdown yang persis sama dengan kalimat berikut:  
   👉 **"Referral is preferred as a precaution"**

4. **Catatan Skenario Tambahan (Override Notes):**  
   Ketikkan teks catatan di bawah ini secara persis ke dalam kotak isian catatan:  
   👉 **"Individual reports unrecorded family history of early diabetes"**

5. **Konfirmasi:**  
   Klik tombol **Confirm Override** untuk menyimpan keputusan akhir Anda.
