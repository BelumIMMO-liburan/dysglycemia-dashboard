# PANDUAN SIDANG & SUPERVISI FELIK: NOTEBOOK 03 (MODEL SELECTION)

> **Catatan:** Dokumen ini **bukan bagian dari naskah skripsi**, melainkan panduan belajar pribadi (cheat-sheet / defense prep) untuk Felik. Bahasa yang digunakan adalah bahasa Indonesia santai campur istilah teknis agar mudah dipahami, diingat, dan diucapkan saat bimbingan atau sidang skripsi.

---

## DAFTAR ISI PERTANYAAN UTAMA DOSEN
1. [Bagaimana cara memilih konfigurasi model terbaik secara objektif?](#1-bagaimana-model-dan-konfigurasi-dipilih)
2. [Kenapa PR-AUC dijadikan metrik seleksi utama (primary selection metric)?](#2-kenapa-pr-auc-jadi-metrik-seleksi-utama)
3. [Apa itu paired bootstrap dan apa gunanya?](#3-apa-itu-paired-bootstrap)
4. [Apa artinya jika confidence interval (CI 95%) melewati angka nol?](#4-apa-arti-confidence-interval-melewati-nol)
5. [Kenapa fitur Expanded dipilih sebagai model utama? Apa burden tambahannya?](#5-kenapa-fitur-expanded-dipilih-dan-apa-burden-tambahannya)
6. [Apa itu kalibrasi probabilitas dan apa arti Brier Score?](#6-apa-itu-kalibrasi-dan-brier-score)
7. [Apa arti calibration slope $< 1.0$?](#7-apa-arti-calibration-slope--10)
8. [Kenapa target sensitivitas ditetapkan pada lantai 90%?](#8-kenapa-target-sensitivitas-90)
9. [Kenapa tidak menargetkan sensitivitas 95% saja agar lebih aman?](#9-kenapa-bukan-95-sensitivitas)
10. [Kenapa sensitivitas 90% BUKAN 'clinical optimum'?](#10-kenapa-90-bukan-clinical-optimum)
11. [Kenapa GAM yang akhirnya di-lock sebagai model utama?](#11-kenapa-gam-yang-di-lock-sebagai-model-utama)

---

## SECTION 1: HIERARKI SELEKSI MODEL & PERAN PR-AUC

### 1. "Ini ngapain?"
Menerapkan aturan hierarki 4 tingkat untuk memilih konfigurasi hyperparameter terbaik di setiap keluarga model:
1. **Peringkat 1 (Utama):** Nilai PR-AUC tertinggi pada OOF development.
2. **Tie-breaker 1:** ROC-AUC tertinggi.
3. **Tie-breaker 2:** Brier score terendah.
4. **Tie-breaker 3:** Model yang lebih simpel (prinsip parsimoni / Occam's razor).
Hasilnya:
* **Logistic Regression:** `L2_C0.1` (PR-AUC: $0.4087$, ROC-AUC: $0.7345$).
* **GAM:** `GAM_splines10_lam10.0` (PR-AUC: $0.4207$, ROC-AUC: $0.7382$).
* **DLNN:** `DLNN_16_8_drop0.0` (PR-AUC: $0.4115$, ROC-AUC: $0.7306$).

### 2. "Kenapa kita lakukan?"
Agar pemilihan model murni berbasis data (*data-driven*) dan terstandarisasi, tanpa bias subjektif peneliti yang memilih konfigurasi sesuka hati.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa kamu pakai PR-AUC sebagai metrik utama seleksi model, bukan ROC-AUC?"*
* **Jawaban Felik:**
  > *"Karena pada populasi skrining komunitas kita, prevalensi disglikemia adalah $23.1\%$ (kelas minoritas), Pak/Bu.*
  > *ROC-AUC memasukkan False Positive Rate yang penyebutnya adalah orang sehat (True Negatives) yang jumlahnya mendominasi ($76.9\%$). Akibatnya, ROC-AUC bisa tampak tinggi meskipun presisi rujukan klinis rendah.*
  > *PR-AUC secara langsung mengevaluasi trade-off antara presisi (PPV) dan sensitivitas (recall) pada pasien yang sakit, sehingga menjadi indikator paling relevan untuk efisiensi rujukan klinis."*

---

## SECTION 2: PAIRED BOOTSTRAP & ARTI CI MELEWATI NOL

### 1. "Ini ngapain?"
Melakukan simulasi **paired bootstrap** sebanyak $2.000$ kali resample (seed 42) pada $3.232$ pasien development untuk menguji apakah selisih performa antar model atau antar set fitur signifikan secara statistik.
* **Paired (Berpasangan):** Pada setiap iterasi bootstrap yang sama, model A dan model B dievaluasi pada sampel pasien yang identik, lalu dihitung selisihnya: $\Delta = \text{Performa}_A - \text{Performa}_B$.

### 2. "Kenapa kita lakukan?"
Nilai metrik seperti ROC-AUC $0.7382$ vs $0.7345$ hanyalah angka tunggal (*point estimate*). Tanpa uji ketidakpastian (confidence interval), kita tidak tahu apakah selisih $+0.0037$ itu kebetulan statistik (*noise*) atau keunggulan yang konsisten.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apa artinya jika 95% Confidence Interval selisih model melewati angka nol (misal delta ROC-AUC GAM vs Logistic: [-0.0017, +0.0095])?"*
* **Jawaban Felik:**
  > *"Artinya selisih performa diskriminasi antara GAM dan Logistic Regression secara statistik tidak dapat dibedakan (compatible with the null hypothesis), Pak/Bu.*
  > *Walaupun GAM unggul secara point estimate ($+0.0037$), rentang keyakinan $95\%$ masih mencakup angka nol dan nilai negatif kecil. Oleh karena itu, di naskah skripsi kami tidak mengklaim GAM secara mutlak lebih superior, melainkan melaporkan bahwa diskriminasi keduanya broadly comparable."*

---

## SECTION 3: CORE VS EXPANDED & FEATURE BURDEN

### 1. "Ini ngapain?"
Membandingkan model Core (5 fitur) vs Expanded (7 fitur) pada peserta development yang sama ($N = 3.232$).
Pada GAM:
* Penambahan fitur menghasilkan $\Delta \text{ROC-AUC} = +0.0080$ (CI 95%: `[0.0013, 0.0147]`) dan $\Delta \text{PR-AUC} = +0.0193$ (CI 95%: `[0.0031, 0.0363]`).
* CI tidak melewati nol, membuktikan ada peningkatan diskriminasi yang positif pada data development.

### 2. "Kenapa kita lakukan?"
Dalam skrining kesehatan masyarakat, menambah pertanyaan atau pengukuran fisik akan menambah beban kerja petugas di lapangan (*measurement burden*).
* **Core (5 fitur):** `age, sex, bmi, hypertension_history, smoking_history`. Sangat mudah, hanya butuh timbangan dan tinggi badan.
* **Expanded (7 fitur):** Menambah pengukuran lingkar pinggang dengan pita meteran (`BMXWAIST`) dan kuesioner duduk 8 pertanyaan (`PAD680`).
Kita harus membuktikan secara ilmiah apakah penambahan beban 2 fitur ini sepadan dengan peningkatan akurasi model.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kalau Expanded menambah beban pengukuran, kenapa tetap dipilih sebagai model primer?"*
* **Jawaban Felik:**
  > *"Karena pada data development, penambahan lingkar pinggang dan durasi duduk memberikan peningkatan PR-AUC yang statistically positive ($+0.0193$, 95% CI tidak melewati nol), Pak/Bu.*
  > *Lingkar pinggang menangkap adipositas sentral (lemak viseral) yang merupakan pemicu utama resistensi insulin, sedangkan durasi duduk merefleksikan gaya hidup sedenter.*
  > *Namun demikian, kami tetap mendokumentasikan model Core dalam skripsi sebagai alternatif ringan (low-burden) untuk implementasi di posyandu atau kios mandiri yang tidak memiliki alat ukur lingkar pinggang."*

---

## SECTION 4: KALIBRASI PROBABILITAS & ARTI SLOPE < 1

### 1. "Ini ngapain?"
Mengevaluasi keandalan probabilitas model menggunakan Brier score, Brier Skill Score (BSS), intercept ($a$), slope ($b$), dan Expected Calibration Error (ECE 10-bin).
Hasil pada Expanded Common:
* **GAM:** Brier $0.1561$, Slope $0.9652$, ECE $0.0106$.
* **Logistic Regression:** Brier $0.1574$, Slope $1.0005$, ECE $0.0169$.
* **DLNN:** Brier $0.1577$, Slope $0.9030$, ECE $0.0135$.

### 2. "Kenapa kita lakukan?"
Model skrining tidak hanya menebak 0 atau 1, tapi mengeluarkan probabilitas risiko (misal $18\%$). Jika probabilitas meleset (misal model memprediksi $40\%$ padahal risiko riil pasien hanya $20\%$), dokter akan salah mengambil keputusan klinis.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apa arti calibration slope bernilai kurang dari 1.0 (misal GAM 0.9652 atau DLNN 0.9030)?"*
* **Jawaban Felik:**
  > *"Nilai calibration slope $< 1.0$ menunjukkan bahwa prediksi probabilitas model cenderung sedikit terlalu ekstrem / overconfident relatif terhadap frekuensi kejadian aktual, Pak/Bu.*
  > *Artinya pada probabilitas tinggi nilainya sedikit terlalu tinggi, dan pada probabilitas rendah nilainya sedikit terlalu rendah. Nilai slope yang ideal adalah tepat 1.0 (seperti Logistic Regression dengan slope 1.0005).*
  > *Namun, nilai GAM sebesar $0.9652$ masih berada dalam kategori 'well-calibrated slope' (mendekati 1) dan memiliki ECE terendah ($0.0106$), sehingga probabilitasnya sangat layak digunakan."*

---

## SECTION 5: LANTAI SENSITIVITAS 90% & THRESHOLD 0.1389

### 1. "Ini ngapain?"
Mengevaluasi 4 lantai sensitivitas pada data OOF: $80\%, 85\%, 90\%, 95\%$.
Untuk lantai $90\%$, algoritma mencari **threshold tertinggi** yang menghasilkan sensitivitas $\ge 90\%$.
Pada GAM Expanded:
* **Threshold terkunci:** **`0.1389`**
* **Sensitivitas dicapai:** **$90.23\%$** (menangkap $674$ dari $747$ orang sakit)
* **Spesifisitas dicapai:** **$42.25\%$**
* **Tingkat rujukan (Referral Rate):** **$65.25\%$**
* **Beban rujukan:** **$3.13$ tes HbA1c per 1 kasus terdeteksi** ($1/\text{PPV}$).

### 2. "Kenapa kita lakukan?"
Tujuan skrining adalah *case-finding* (menjaring orang sakit sebanyak-banyaknya).
Jika kita menaikkan sensitivitas:
* Dari $85\% \to 90\%$: sensitivitas naik $+5.22\%$ dengan rujukan hanya naik sedikit ($59.1\% \to 65.3\%$). Ini trade-off yang efisien.
* Dari $90\% \to 95\%$: sensitivitas hanya naik $+4.82\%$, tetapi angka rujukan melonjak drastis ke $76.67\%$ (merujuk lebih dari 3/4 populasi!). Kapasitas lab puskesmas akan jebol karena kebanjiran rujukan.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa kamu kunci di 90%? Kenapa bukan 95%? Dan apakah 90% itu angka optimal klinis?"*
* **Jawaban Felik:**
  > *"Angka 90% adalah **pre-specified research operating point** (titik operasi riset yang ditetapkan di awal), bukan angka optimal klinis mutlak, Pak/Bu.*
  > *Di atas 90%, terjadi lonjakan False Positives yang sangat tajam sehingga membebani sistem rujukan laboratorium secara berlebihan.*
  > *Kami menetapkan lantai 90% sebagai skenario skrining konservatif yang memprioritaskan penemuan kasus baru, lalu mengunci threshold 0.1389 secara permanen sebelum test set dibuka."*

---

## SECTION 6: PRE-TEST SPECIFICATION LOCK

### 1. "Ini ngapain?"
Membekukan seluruh parameter model primer ke dalam dokumen locked (`lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md`):
* Model: GAM (`splines10_lam10.0`)
* Fitur: 7 prediktor Expanded
* Threshold: `0.1389`
* Comparator: Logistic Regression (`L2_C0.1`, threshold `0.1389`) dan DLNN (`16_8_drop0.0`, threshold `0.1419`).

### 2. "Kenapa kita lakukan?"
Ini adalah **garis batas metodologis paling sakral dalam skripsi ini**.
Begitu dokumen ini di-lock, kita berjanji secara ilmiah bahwa **tidak akan ada lagi perubahan parameter atau threshold apa pun** setelah melihat hasil test set.
Ini menjamin riset Felik bebas dari *p-hacking*, manipulasi threshold post-hoc, atau kecurangan model.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apa jaminan kamu tidak mengubah threshold setelah melihat nilai test set?"*
* **Jawaban Felik:**
  > *"Dokumen spesifikasi kami telah dibekukan dalam file `FINAL_MODEL_SPECIFICATION_LOCKED.md` dengan hash SHA256 `7d2a5eb9c349dabf...` sebelum test set dibuka, Pak/Bu.*
  > *Threshold 0.1389 berasal murni dari kalkulasi OOF development. Di Notebook 04, test set hanya dievaluasi satu kali (single forward pass) menggunakan threshold beku ini tanpa penyesuaian sedikit pun."*
