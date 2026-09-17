# PANDUAN SIDANG & SUPERVISI FELIK: NOTEBOOK 02 (MODEL DEVELOPMENT)

> **Catatan:** Dokumen ini **bukan bagian dari naskah skripsi**, melainkan panduan belajar pribadi (cheat-sheet / defense prep) untuk Felik. Bahasa yang digunakan adalah bahasa Indonesia santai campur istilah teknis agar mudah dipahami, diingat, dan diucapkan saat bimbingan atau sidang skripsi.

---

## DAFTAR ISI PERTANYAAN UTAMA DOSEN
1. [Apa beda training CV dan final training?](#1-apa-beda-training-cv-dan-final-training)
2. [Apa itu 5-fold cross-validation dan OOF prediction?](#2-apa-itu-5-fold-cross-validation-dan-oof-prediction)
3. [Kenapa test set tidak boleh dipakai untuk memilih model?](#3-kenapa-test-set-tidak-boleh-dipakai-pilih-model)
4. [Kenapa StandardScaler harus di-fit HANYA dari train fold?](#4-kenapa-scaler-harus-fit-hanya-dari-train-fold)
5. [Kenapa Logistic Regression tetap dipakai sebagai baseline?](#5-kenapa-logistic-regression-tetap-dipakai)
6. [Kenapa memilih Generalized Additive Model (GAM)?](#6-kenapa-memilih-gam)
7. [Kenapa menguji Deep Learning (DLNN)?](#7-kenapa-menguji-dlnn)
8. [Apa itu PR-AUC dan kenapa tidak cukup pakai Accuracy atau ROC-AUC saja?](#8-apa-itu-pr-auc-dan-kenapa-bukan-accuracy)
9. [Kenapa threshold 0.5 TIDAK OTOMATIS dipakai dalam skrining?](#9-kenapa-threshold-05-tidak-otomatis-dipakai)
10. [Kenapa Deep Learning (DLNN) tidak otomatis menang melawan GAM?](#10-kenapa-dlnn-tidak-otomatis-menang)

---

## SECTION 1: MASTER SPLIT & PARTISI DEVELOPMENT

### 1. "Ini ngapain?"
Membagi data canonical expanded ($N = 4.044$) menjadi dua partisi tetap menggunakan `master_split.csv`:
* **Development Partition (80%):** $N = 3.232$ orang.
* **Held-Out Final Test Partition (20%):** $N = 812$ orang.
Notebook 02 **hanya bekerja pada data development ($N = 3.232$)**. Data test set sama sekali tidak dibuka atau dihitung di sini.

### 2. "Kenapa kita lakukan?"
Agar evaluasi model jujur secara sains. Dalam machine learning medis, jika test set disentuh saat eksplorasi model atau pemilihan hyperparameter, akan terjadi *data snooping* / *test set leakage*. Model akan tampak hebat di atas kertas, tapi gagal saat diuji ke pasien baru di dunia nyata.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa kamu memisahkan data 80:20 di awal? Kenapa tidak langsung cross-validation pada seluruh 4.044 orang?"*
* **Jawaban Felik:**
  > *"Untuk menjaga standar integritas konfirmatori tertinggi, Pak/Bu. Data development 80% ($N = 3.232$) digunakan untuk seluruh siklus eksplorasi, tuning hyperparameter, dan validasi silang (5-fold CV).*
  > *Sedangkan data test 20% ($N = 812$) dikunci rapat sebagai 'held-out test set' yang bertindak sebagai pasien masa depan yang sama sekali belum pernah dilihat oleh algoritma. Ini mencegah bias optimisme (overfitting)."*

### 4. "Yang jangan sampai gue salah ngomong"
* **JANGAN BILANG:** *"Di notebook ini saya sudah tahu akurasi test set saya 86%."* (Salah fatal! Di notebook 02, test set belum pernah dibuka sama sekali!).

---

## SECTION 2: 5-FOLD STRATIFIED CV & OOF PREDICTIONS

### 1. "Ini ngapain?"
Membagi $3.232$ peserta development menjadi 5 fold terstratifikasi ($\approx 646$ orang per fold, prevalensi disglikemia dipertahankan $\approx 23.1\%$).
Pada setiap putaran fold $k$:
* 4 fold ($\approx 2.585$ orang) dipakai melatih model (training fold).
* 1 fold ($\approx 647$ orang) diprediksi probabilitasnya (validation fold).
Hasil prediksi probabilitas dari masing-masing fold validasi dikumpulkan menjadi satu vektor utuh berukuran $3.232$ yang disebut **Out-of-Fold (OOF) predictions**.

### 2. "Kenapa kita lakukan?"
Karena OOF prediction mencerminkan performa model terhadap data yang **tidak pernah dilihat saat training**. Setiap baris dari $3.232$ orang diprediksi oleh model yang tidak dilatih menggunakan baris tersebut. Ini memberikan estimasi generalisasi yang tidak bias tanpa menyentuh test set.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Apa bedanya training CV dengan final training?"*
* **Jawaban Felik:**
  > *"Pada training CV, kita melatih 5 model terpisah pada 4/5 data untuk mengukur stabilitas dan memilih konfigurasi terbaik melalui OOF predictions.*
  > *Setelah arsitektur terbaik terpilih di akhir Phase 4, barulah kita melakukan 'Final Training', yaitu melatih SATU model tunggal menggunakan SELURUH data development ($100\%$ dari $3.232$ orang) sebelum nantinya diuji ke test set."*

---

## SECTION 3: PREPROCESSING & DATA LEAKAGE PREVENTION

### 1. "Ini ngapain?"
Menstandarkan variabel kontinu (`age, bmi, waist_cm, sedentary_minutes_day`) menggunakan `StandardScaler`, dan mengonversi variabel biner (`sex, hypertension_history, smoking_history`) menjadi $\{0, 1\}$.
Proses `fit()` scaler dilakukan **HANYA pada data training fold**. Data validasi hanya di-`transform()`.

### 2. "Kenapa kita lakukan?"
Jika kita melakukan `fit()` scaler pada seluruh $3.232$ orang sebelum cross-validation, informasi rata-rata ($\mu$) dan standar deviasi ($\sigma$) dari fold validasi akan bocor ke fold training (*pre-split leakage*).

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa kamu repot-repot fit scaler di dalam setiap loop fold? Kenapa tidak scale di awal saja?"*
* **Jawaban Felik:**
  > *"Karena jika kita menghitung mean dan standar deviasi pada seluruh dataset sebelum split, itu merupakan bentuk kebocoran informasi (data leakage), Pak/Bu.*
  > *Di dunia nyata, kita tidak pernah tahu nilai mean pasien yang akan datang besok. Standar machine learning yang benar mewajibkan scaler hanya mempelajari parameter statistik dari data latih fold tersebut."*

---

## SECTION 4: TIGA KELUARGA MODEL (LOGISTIC, GAM, DLNN)

### 1. "Ini ngapain?"
Membandingkan tiga paradigma pemodelan:
1. **Logistic Regression (L2):** Model parametrik linier klasik dengan penalti Ridge ($C \in \{0.01, 0.1, 1.0, 10.0\}$).
2. **Generalized Additive Model (GAM):** Model aditif semi-parametrik dengan P-splines kubik 10 simpul dan smoothing $\lambda \in \{0.01, 0.1, 1.0, 10.0\}$.
3. **Deep Learning Neural Network (DLNN):** Multi-Layer Perceptron (arsitektur $16 \to 8$ atau $32 \to 16$, Dropout $0.0$ / $0.2$, aktivasi ReLU, optimizer Adam, early stopping).

### 2. "Kenapa kita lakukan?"
Riset ini ingin menjawab pertanyaan ilmiah fundamental: **Apakah hubungan biologis faktor risiko non-laboratorium bersifat non-linear, dan apakah kompleksitas komputasi model non-linear terbayar dengan peningkatan akurasi skrining?**
* Logistic Regression = apakah garis lurus log-odds sudah cukup?
* GAM = apakah kurva spline non-linear yang dapat diinterpretasi memberikan keuntungan?
* DLNN = apakah interaksi representasi dalam multi-layer neural network memberikan keunggulan ekstra?

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa kamu pakai GAM? Apa kelebihannya dibanding Logistic Regression dan Random Forest?"*
* **Jawaban Felik:**
  > *"GAM menggabungkan dua keunggulan sekaligus, Pak/Bu: **fleksibilitas kurva non-linear** seperti machine learning modern, tetapi tetap mempertahankan **interpretabilitas aditif** seperti regresi linear.*
  > *Hubungan antara usia, BMI, lingkar pinggang dengan risiko disglikemia bukanlah garis lurus monoton, melainkan kurva berbentuk S atau eksponensial setelah ambang tertentu. GAM dapat menangkap bentuk kurva biologis ini secara mulus melalui fungsi spline $f(x_i)$ tanpa menjadi kotak hitam (black-box) seperti Random Forest atau Deep Learning."*

---

## SECTION 5: METRIK EVALUASI: KENAPA PR-AUC & BUKAN ACCURACY?

### 1. "Ini ngapain?"
Mengevaluasi OOF predictions menggunakan **ROC-AUC**, **PR-AUC (Average Precision)**, dan **Brier Score**, bukan menggunakan Accuracy.

### 2. "Kenapa kita lakukan?"
Data skrining kita memiliki ketidakseimbangan kelas ($23.1\%$ disglikemia vs $76.9\%$ normal).
* **Kelemahan Accuracy:** Jika sebuah model malas menebak semua orang "Normal", akurasinya sudah otomatis $76.9\%$, tapi model tersebut gagal mendeteksi $100\%$ orang sakit (sensitivitas 0%). Accuracy sangat menyesatkan untuk data medis tidak seimbang.
* **Kelebihan PR-AUC:** Mengukur trade-off langsung antara Precision (PPV) dan Recall (Sensitivity) hanya pada kelas positif (disglikemia), tanpa terdistorsi oleh tingginya jumlah orang sehat (True Negatives).

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa metrik seleksi utama kamu PR-AUC, bukan ROC-AUC?"*
* **Jawaban Felik:**
  > *"Karena prevalensi disglikemia pada populasi skrining komunitas adalah $23.1\%$, Pak/Bu. ROC-AUC memasukkan False Positive Rate yang pembaginya adalah jumlah orang sehat (True Negatives) yang sangat banyak, sehingga nilai ROC-AUC bisa tampak tinggi semu.*
  > *PR-AUC secara khusus menyoroti efisiensi rujukan klinis: dari seluruh orang yang diprediksi berisiko tinggi, berapa proporsi yang benar-benar mengalami disglikemia di setiap level sensitivitas."*

---

## SECTION 6: KENAPA THRESHOLD 0.5 GAGAL TOTAL UNTUK SKRINING?

### 1. "Ini ngapain?"
Membuktikan secara matematis bahwa memotong probabilitas pada ambang default **$0.50$** menghasilkan sensitivitas yang sangat buruk ($12.85\%$).

### 2. "Kenapa kita lakukan?"
Banyak mahasiswa salah kaprah mengira threshold biner harus selalu 0.5.
Pada data dengan prevalensi baseline $23\%$, model yang terkalibrasi baik akan menghasilkan probabilitas berkisar antara $0.05$ sampai $0.45$. Sangat sedikit orang yang mencapai probabilitas $> 0.50$.
Jika dipaksa memakai cut-off 0.5:
* Model hanya menemukan 96 orang disglikemia dari total 747 orang sakit ($87\%$ orang sakit terlewatkan!).
* Skrining kesehatan masyarakat bertujuan menangkap orang sakit sebanyak mungkin (sensitivitas tinggi $\ge 90\%$), sehingga threshold harus diturunkan secara klinis (dioptimasi di Notebook 03).

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Kenapa threshold model kamu bukan 0.5? Apakah kamu sengaja otak-atik threshold supaya akurasi kelihatan bagus?"*
* **Jawaban Felik:**
  > *"Sama sekali bukan mengotak-atik, Pak/Bu, melainkan kalibrasi keputusan operasional (operational decision threshold).*
  > *Threshold 0.5 hanya cocok jika prevalensi penyakit $50:50$ dan biaya melewatkan orang sakit sama dengan biaya merujuk orang sehat. Dalam skrining pencegahan disglikemia di komunitas, melewatkan pasien prediabetes jauh lebih berbahaya daripada merujuk orang sehat untuk tes darah.*
  > *Oleh karena itu, di Notebook 03 threshold diturunkan secara terencana untuk menjamin batas lantai sensitivitas $90\%$."*

---

## SECTION 7: HASIL DEVELOPMENT & PERFORMA DLNN

### 1. "Ini ngapain?"
Menunjukkan hasil OOF pada Expanded Common ($N = 3.232$):
* **GAM (`splines10_lam10.0`):** ROC-AUC = $0.7382$, PR-AUC = $0.4207$, Brier = $0.1561$ (Peringkat 1).
* **Logistic Regression (`L2_C0.1`):** ROC-AUC = $0.7345$, PR-AUC = $0.4087$, Brier = $0.1574$.
* **DLNN (`16_8_drop0.0`):** ROC-AUC = $0.7306$, PR-AUC = $0.4115$, Brier = $0.1577$.

### 2. "Kenapa DLNN tidak menang?"
Deep Learning unggul pada data berdimensi tinggi seperti citra medis atau teks (jutaan parameter). Pada data tabular epidemiologi dengan 7 fitur non-laboratorium dan sampel ribuan orang:
1. Deep learning rentan over-parameterized.
2. Tidak ada representasi hierarkis spasial yang perlu dipelajari.
3. GAM dengan kurva spline regulasi justru bekerja optimal menangkap non-linearitas biologis tanpa overfitting.

### 3. "Kalau dosen nanya, jawab apa?"
* **Dosen:** *"Masa Deep Learning kalah sama GAM? Bukannya Deep Learning algoritma paling canggih?"*
* **Jawaban Felik:**
  > *"Temuan empiris ini sejalan dengan konsensus literatur machine learning tabular terkini (seperti Grinsztajn et al., NeurIPS 2022), Pak/Bu.*
  > *Pada data tabular klinis berfitur ringkas ($k = 7$), arsitektur neural network yang kompleks tidak memberikan keunggulan representasional dibandingkan model aditif berbasis spline seperti GAM.*
  > *Justru kesimpulan penting skripsi ini adalah membuktikan bahwa model non-linear yang dapat diinterpretasi (GAM) memberikan performa diskriminasi yang lebih tinggi dengan komputasi yang jauh lebih ringan dan transparan."*
