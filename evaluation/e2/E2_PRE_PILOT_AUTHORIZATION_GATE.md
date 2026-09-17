# Gerbang Otorisasi Pra-Pelaksanaan Pilot (Pre-Pilot Authorization Gate)
## Pengendalian Kepatuhan Tata Kelola & Persetujuan Institusional Sebelum Kontak Partisipan

**Kode Dokumen:** `E2-AUTH-GATE-V1.0`  
**Versi Paket Evaluasi:** `1.0`  
**Protokol Acuan:** `E1-PROTOCOL-2026-V1.0.3` (Status: Terkunci / Frozen)  
**Status Gerbang Saat Ini:** 🔴 **NOT AUTHORIZED FOR PARTICIPANT CONTACT**  
*(TIDAK DIIZINKAN UNTUK MENGHUBUNGI ATAU MEREKRUT PARTISIPAN)*

---

### 1. Tujuan dan Fungsi Gerbang
Sesuai prinsip tata kelola riset (*Research Governance*), fase E2 bertugas menyiapkan seluruh paket operasional, instrumen, dan arsitektur data, namun **SECARA EKSPLISIT DILARANG** memulai rekrutmen, kontak partisipan, atau pengumpulan data manusia sebelum seluruh butir otorisasi institusional di bawah ini disetujui secara formal.

---

### 2. Matriks Butir Kepatuhan Otorisasi

| No | Butir Persyaratan Otorisasi | Status Otorisasi | Bukti / Catatan Verifikasi |
| :-: | :--- | :---: | :--- |
| 1 | **Persetujuan Dosen Pembimbing untuk Pelaksanaan Pilot ($N=3\text{--}5$)** | **PENDING** | Menunggu penelaahan resmi paket instrumen E2 oleh dosen pembimbing tugas akhir. |
| 2 | **Penetapan Kebutuhan Komite Etik Penelitian Institusional** | **PENDING** | Menunggu konfirmasi formal fakultas/universitas apakah evaluasi usability berisiko minimal memerlukan *Ethical Clearance* penuh atau *Exemption Review*. |
| 3 | **Persetujuan Etik Penelitian (jika diwajibkan oleh butir 2)** | **PENDING** | Bergantung pada keputusan butir 2. Dokumen registrasi siap diajukan. |
| 4 | **Persetujuan Naskah Lembar Informasi Peserta (`E2_PARTICIPANT_INFORMATION_SHEET_ID.md`)** | **PENDING** | Butir informasi telah siap; membutuhkan persetujuan supervisor terhadap rincian kontak resmi. |
| 5 | **Persetujuan Naskah Formulir Persetujuan (`E2_CONSENT_FORM_DRAFT_ID.md`)** | **PENDING** | Menunggu konfirmasi apakah menggunakan draf ini atau template standar fakultas. |
| 6 | **Persetujuan Pilihan Platform Kuesioner Digital (`E2_SURVEY_PLATFORM_DECISION.md`)** | **PENDING** | Menunggu penetapan platform oleh supervisor (Google Forms institusi / MS Forms). |
| 7 | **Verifikasi Kesiapan Teknis & Kebekuan Prototipe (`research-prototype-v1.0`)** | **PASSED (VERIFIED)** | 144 unit tests passing, integritas 4 hash model/preprocessor terverifikasi 100%. |
| 8 | **Verifikasi Prosedur Isolasi Sesi Basis Data (`db_session_template.sqlite3`)** | **PASSED (VERIFIED)** | Prosedur duplikasi dan verifikasi hitungan nol baris teruji secara deterministik. |

---

### 3. Kriteria Pembukaan Gerbang Menjadi "AUTHORIZED FOR PILOT CONTACT"
Gerbang ini **HANYA DAPAT** diubah statusnya menjadi:
🟢 **AUTHORIZED FOR PILOT CONTACT**  
apabila:
1. Butir 1 (Persetujuan Pembimbing) telah ditandatangani / dikonfirmasi secara tertulis.
2. Butir 2 & 3 (Penetapan & Persetujuan Etik) telah diterbitkan atau secara formal dinyatakan tidak memerlukan kaji etik lanjutan (*ethics exemption*).
3. Seluruh placeholder `[TO BE COMPLETED AFTER INSTITUTIONAL REVIEW]` pada lembar informasi peserta dan persetujuan telah digantikan dengan informasi definitif.
4. Supervisor telah menandatangani formulir peluncuran pilot.

---

### 4. Larangan Operasional Selama Status "NOT AUTHORIZED"
Selama dokumen ini berstatus **NOT AUTHORIZED FOR PARTICIPANT CONTACT**, maka:
- ❌ **DILARANG** menyebarkan undangan atau pamflet rekrutmen peserta pilot.
- ❌ **DILARANG** meminta calon peserta mengisi formulir persetujuan.
- ❌ **DILARANG** mengumpulkan data interaksi manusia atau respon kuesioner.
- ❌ **DILARANG** mengklaim bahwa studi telah memiliki persetujuan etik sebelum bukti resmi diperoleh.

*Pengesahan Fase E2:*  
Dokumen ini mengunci batas operasional bahwa seluruh persiapan instrumen telah tuntas secara teknis dan metodologis, dengan gerbang keselamatan partisipan tetap terkunci rapat.
