# PANDUAN SIDANG & SUPERVISI FELIK: NOTEBOOK 04 (FINAL TEST EVALUATION)

> **Catatan:** Dokumen ini **bukan bagian dari naskah skripsi**, melainkan panduan belajar pribadi (cheat-sheet / defense prep) untuk Felik. Bahasa yang digunakan adalah bahasa Indonesia santai campur istilah teknis agar mudah dipahami, diingat, dan diucapkan saat bimbingan atau sidang skripsi.

---

## DAFTAR ISI PERTANYAAN PALING KRITIS PENGUJI
1. [Apa sebenarnya held-out final test set itu?](#1-apa-sebenarnya-final-test)
2. [Kenapa test set HANYA BOLEH DIBUKA SATU KALI?](#2-kenapa-test-set-hanya-boleh-dibuka-sekali)
3. [Kenapa sensitivitas final GAM 'cuma' 86.39% padahal di development 90.23%?](#3-kenapa-sensitivitas-final-turun-ke-8639)
4. [Apakah sensitivitas 86.39% berarti model kita gagal?](#4-apakah-model-kita-gagal)
5. [Kenapa threshold-nya tidak diturunkan saja supaya sensitivitasnya pas 90%?](#5-kenapa-threshold-tidak-diturunkan-post-hoc)
6. [Apakah GAM 'menang mutlak' melawan Logistic Regression?](#6-apakah-gam-menang-mutlak)
7. [Kenapa ROC-AUC Logistic Regression (0.7288) sedikit lebih tinggi dari GAM (0.7277)?](#7-kenapa-roc-auc-logistic-sedikit-lebih-tinggi)
8. [Kalau begitu, kenapa GAM tetap dipertahankan sebagai model primer?](#8-kenapa-gam-tetap-primary-model)
9. [Apa kesimpulan akhir tentang Deep Learning (DLNN)?](#9-apa-kesimpulan-tentang-dlnn)
10. [Apa arti klinis dari 522 orang direfer dan 26 kasus missed?](#10-apa-arti-522-orang-direfer-dan-26-missed)
11. [Apa arti False Positive (357 orang) dalam konteks skrining kesehatan?](#11-apa-arti-false-positive-dalam-skrining)
12. [Kenapa model ini BUKAN alat diagnosis?](#12-kenapa-ini-bukan-diagnosis)
13. [Kenapa hasil riset ini TIDAK BOLEH diklaim berlaku ke populasi Indonesia?](#13-kenapa-tidak-boleh-klaim-ke-indonesia)
14. [Apa yang BOLEH dan TIDAK BOLEH diklaim dari data NHANES?](#14-apa-yang-boleh-dan-tidak-boleh-diklaim)

---

## SECTION 1: HELD-OUT TEST SET & INTEGRITAS SATU KALI BUKA

### 1. "Ini ngapain?"
Mengevaluasi performa model final pada $N = 812$ orang peserta test set yang belum pernah dilihat sama sekali selama pembuatan model.
Proses ini dilakukan **hanya satu kali jalan (single forward pass)** menggunakan threshold yang sudah dibekukan (`0.1389`). Di Notebook 04, kita **hanya membaca file prediksi yang sudah beku** (`final_test_predictions.csv`), tanpa melatih model lagi.

### 2. "Kenapa kita lakukan?"
Untuk menjaga kejujuran ilmiah tingkat tertinggi (*gold standard confirmation*).
Jika peneliti membuka test set berkali-kali lalu mengubah-ubah model atau menggeser-geser threshold agar nilainya bagus di test set, itu namanya **kebocoran data post-hoc (data snooping / p-hacking)**.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa di Notebook 04 kamu tidak memanggil `model.fit()` atau `model.predict()`?"*
* **Jawaban Felik:**
  > *"Karena evaluasi test set konfirmatori telah dijalankan satu kali secara permanen pada Phase 5, Pak/Bu.*
  > *Notebook 04 bertindak sebagai **audit forensik dan verifikasi reproduksibilitas independen** terhadap vektor prediksi beku tersebut.*
  > *Menjalankan ulang fitting atau mengubah prediksi setelah test set dibuka melanggar protokol tata kelola penelitian terkunci (locked protocol governance)."*

---

## SECTION 2: SENSITIVITAS 86.39% & KENAPA TIDAK BOLEH DIUBAH

### 1. "Ini ngapain?"
Melaporkan bahwa threshold `0.1389` yang di development menghasilkan sensitivitas $90.23\%$, saat diuji ke test set menghasilkan sensitivitas **$86.39\%$** (menangkap $165$ dari $191$ kasus disglikemia, 95% CI: `[81.19%, 90.96%]`).

### 2. "Kenapa kita lakukan?"
Karena ini adalah **fakta empiris nyata**.
Ketika threshold beku diterapkan pada sampel acak baru, variasi sampling acak adalah hal yang wajar dalam epidemiologi.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Loh, Felik, target kamu kan sensitivitas 90%. Kenapa di test set cuma dapat 86.39%? Berarti model kamu gagal dong?"*
* **Jawaban Felik:**
  > *"Sama sekali bukan gagal, Pak/Bu, melainkan variasi sampling alami pada data uji independen.*
  > *Target 90% adalah **titik operasi riset yang diderivasi dari data development**.*
  > *Pada test set, interval kepercayaan 95% bootstrap berada di rentang **81.19% hingga 90.96%**, yang berarti angka 90% masih tercakup dalam rentang keyakinan.*
  > *Secara metodologis kami menyatakan secara jujur: 'The 90% development sensitivity target was not reproduced at the final-test point estimate'. Penurunan kecil point estimate ini adalah bukti otentik generalisasi prospektif yang tidak mengalami overfitting."*

* **Dosen:** *"Kalau begitu kenapa tidak kamu turunkan saja threshold-nya dari 0.1389 ke misal 0.12 supaya pas 90% di test set?"*
* **Jawaban Felik:**
  > *"Itu tindakan yang dilarang keras dalam metodologi machine learning medis, Pak/Bu.*
  > *Mengubah threshold setelah melihat hasil test set disebut **post-hoc threshold tuning (data snooping)**. Jika kita menurunkan threshold setelah melihat test set, kita menipu diri sendiri karena di dunia nyata kita tidak pernah tahu label pasien masa depan.*
  > *Kekuatan ilmiah skripsi ini justru terletak pada kedisiplinan kami menjaga threshold tetap beku."*

---

## SECTION 3: GAM VS LOGISTIC REGRESSION & DLNN

### 1. "Ini ngapain?"
Membandingkan ketiga model pada test set ($N = 812$):
* **GAM:** ROC-AUC $0.7277$ | PR-AUC **$0.4503$** | Brier $0.1587$ | Sens $86.39\%$ | Spec **$42.51\%$** | Referral **$64.29\%$**
* **Logistic Regression:** ROC-AUC **$0.7288$** | PR-AUC $0.4407$ | Brier $0.1587$ | Sens $86.39\%$ | Spec $40.74\%$ | Referral $65.64\%$
* **DLNN:** ROC-AUC $0.7200$ | PR-AUC $0.4214$ | Brier $0.1609$ | Sens $86.91\%$ | Spec $41.71\%$ | Referral $65.02\%$

### 2. "Kenapa kita lakukan?"
Untuk menjawab secara jujur model mana yang paling layak direkomendasikan untuk implementasi skrining.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Liat nih, ROC-AUC Logistic Regression (0.7288) lebih tinggi dari GAM (0.7277). Kenapa kamu masih mempertahankan GAM sebagai model primer? GAM kalah dong?"*
* **Jawaban Felik:**
  > *"Selisih ROC-AUC tersebut hanya $-0.0011$ (kurang dari $0.1\%$) dengan interval kepercayaan 95% `[-0.0127, +0.0099]` yang melewati nol, yang berarti secara statistik performa keduanya setara (broadly comparable), Pak/Bu.*
  > *Namun GAM unggul dalam aspek-aspek klinis yang sangat krusial:*
  > *1. **PR-AUC GAM lebih tinggi (0.4503 vs 0.4407):** menunjukkan presisi rujukan yang lebih baik.*
  > *2. **Spesifisitas GAM lebih tinggi (42.51% vs 40.74%):** selisih $+1.77\%$ dengan 95% CI `[0.0000, 0.0349]` yang positif signifikan.*
  > *3. **Beban Rujukan Lebih Rendah (64.29% vs 65.64%):** Dengan sensitivitas yang sama persis (keduanya menangkap tepat 165 kasus), GAM berhasil menyaring 11 orang sehat lebih banyak daripada Logistic Regression.*
  > *Selain itu, GAM memiliki kurva spline yang transparan untuk menjelaskan pengaruh usia, BMI, dan lingkar pinggang secara visual kepada dokter."*

* **Dosen:** *"Bagaimana dengan Deep Learning (DLNN)?"*
* **Jawaban Felik:**
  > *"DLNN memiliki performa terendah di ketiga metrik (ROC-AUC 0.7200, PR-AUC 0.4214). Kesimpulan ilmiah kami menyatakan bahwa: **DLNN tidak menunjukkan keunggulan prediktif yang dapat membenarkan kompleksitas tambahannya pada tugas skrining tabular ini**."*

---

## SECTION 4: KALIBRASI & LOGISTIC SLOPE TERBAIK

### 1. "Ini ngapain?"
Melaporkan kalibrasi pada test set:
* **GAM:** Slope $0.9425$, ECE $0.0238$
* **Logistic Regression:** Slope **$1.0013$**, ECE $0.0124$
* **DLNN:** Slope $0.9208$, ECE $0.0113$

### 2. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apakah kalibrasi GAM yang terbaik di test set?"*
* **Jawaban Felik:**
  > *"Tidak, Pak/Bu. Di test set, **Logistic Regression menunjukkan slope kalibrasi yang paling mendekati 1.0 (1.0013)** dan ECE yang lebih rendah (0.0124).*
  > *GAM memiliki slope 0.9425 yang menunjukkan kecenderungan prediksi sedikit terlalu ekstrem, meskipun masih dalam batas 'well-calibrated'. Ini kami laporkan secara objektif tanpa ditutup-tutupi."*

---

## SECTION 5: ARTI KLINIS SCREENING FLOW (522 RUJUKAN, 26 MISSED)

### 1. "Ini ngapain?"
Membaca matriks konfusi GAM pada $812$ warga komunitas:
* **522 orang ($64.29\%$) direferensikan** untuk tes darah HbA1c di lab (Screen-Positive).
* **290 orang ($35.71\%$) dinyatakan aman / tidak direferensikan** (Screen-Negative).
* Dari $191$ orang yang sebenarnya sakit disglikemia: **$165$ orang berhasil ditangkap ($86.39\%$)**, dan **$26$ orang terlewatkan ($13.61\%$)**.
* Dari $621$ orang sehat: **$264$ orang berhasil disaring tanpa tes lab ($42.51\%$)**, dan **$357$ orang False Positive**.

### 2. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Ada 357 orang False Positive (orang sehat tapi dirujuk ke lab). Bukannya itu bahaya atau buang-buang uang?"*
* **Jawaban Felik:**
  > *"Dalam konteks skrining pencegahan primer, False Positive adalah **biaya yang wajar dan aman (safe false alarm)**, Pak/Bu.*
  > *Tahap 1 hanyalah kuesioner dan timbangan berat badan. Jika seseorang False Positive di Tahap 1, konsekuensinya hanyalah mereka dirujuk ke lab puskesmas untuk tes darah HbA1c (Tahap 2).*
  > *Di Tahap 2, hasil tes darahnya akan menunjukkan bahwa gula darahnya normal, dan pasien merasa lega.*
  > *Yang paling berbahaya dalam skrining justru adalah **False Negative (26 orang yang missed)**, karena mereka mengira dirinya sehat padahal gula darahnya sudah merusak pembuluh darah.*
  > *Dengan efisiensi rujukan **3.16 tes per 1 kasus terdeteksi**, puskesmas hanya perlu melakukan sekitar 3 tes HbA1c untuk menemukan 1 orang disglikemia baru. Ini penghematan besar dibanding melakukan tes darah massal ke seluruh 812 warga."*

---

## SECTION 6: BATASAN KLAIM RISET & POPULASI INDONESIA

### 1. "Ini ngapain?"
Menegaskan batas keabsahan klaim ilmiah riset di Bab 5 dan Kesimpulan.

### 2. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apakah model kamu ini bisa langsung dipasang di Puskesmas di Jakarta atau pedesaan Indonesia?"*
* **Jawaban Felik:**
  > *"Secara etika ilmiah dan regulasi medis: **BELUM BISA, Pak/Bu**.*
  > *Model ini dilatih dan divalidasi menggunakan data survei NHANES Amerika Serikat. Karakteristik genetik, batas cut-off lingkar pinggang populasi Asia (WHO merekomendasikan cut-off lebih rendah untuk Asia), serta pola diet masyarakat Indonesia berbeda.*
  > *Skripsi ini membuktikan **validitas metodologis dan komparasi algoritma skrining bertingkat**.*
  > *Untuk implementasi nyata di Indonesia, arsitektur pipeline kami harus di-retrain atau dikalibrasi ulang menggunakan data lokal Indonesia (seperti data SKI jika kelak terbuka, atau data kohort puskesmas)."*

* **Dosen:** *"Apakah hasil ini mewakili seluruh populasi Amerika Serikat?"*
* **Jawaban Felik:**
  > *"Tidak, Pak/Bu. Karena pemodelan machine learning kami dilakukan pada level perorangan yang tidak dibobot (unweighted), kami **tidak mengklaim estimasi prevalensi representatif nasional Amerika Serikat**. Evaluasi kami murni mengukur akurasi prediktif komputasional pada kohort studi."*
