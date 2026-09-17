# PANDUAN SIDANG & SUPERVISI FELIK: NOTEBOOK 01 (DATA PREPARATION)

> **Catatan:** Dokumen ini **bukan bagian dari naskah skripsi**, melainkan panduan belajar pribadi (cheat-sheet / defense prep) untuk Felik. Bahasa yang digunakan adalah bahasa Indonesia santai campur istilah teknis agar mudah dipahami, diingat, dan diucapkan saat bimbingan atau sidang skripsi.

---

## DAFTAR ISI PERTANYAAN UTAMA DOSEN
1. [Kenapa pindah ke NHANES dan bukan data Indonesia?](#1-kenapa-nhanes-dan-bukan-data-indonesia)
2. [Apa itu SEQN dan bagaimana cara merge-nya?](#2-apa-fungsi-seqn-dan-cara-merge)
3. [Kenapa orang yang sudah tahu diabetes / prediabetes harus dibuang (Cohort E)?](#3-kenapa-exclude-orang-yang-sudah-tahu-diabetesprediabetes)
4. [Apa sebenarnya target model kita? Kenapa HbA1c $\ge 5.7\%$?](#4-apa-target-model-dan-kenapa-hba1c--57)
5. [Kenapa ini BUKAN prediksi diabetes di masa depan (future diabetes prediction)?](#5-kenapa-bukan-future-diabetes-prediction)
6. [Apa bedanya Core Predictors vs Expanded Predictors?](#6-apa-beda-core-vs-expanded-predictors)
7. [Kenapa nilai 9999 pada PAD680 tidak boleh dianggap angka biasa?](#7-kenapa-pad680-9999-harus-jadi-nan-rekon-4066-vs-4044)
8. [Kenapa variabel laboratorium TIDAK BOLEH masuk ke prediktor Stage 1 (Data Leakage)?](#8-kenapa-variabel-lab-tidak-boleh-masuk-prediktor-stage-1)
9. [Kenapa survey weights disimpan tapi tidak dijadikan fitur ML?](#9-kenapa-survey-weights-disimpan-tapi-tidak-jadi-fitur)
10. [Kenapa ukuran sampel akhir complete-case tepat 4.044 orang?](#10-kenapa-n-akhir-expanded-tepat-4044-orang)

---

## SECTION 1: LATAR BELAKANG & SUMBER DATA

### A. Ini ngapain?
Menjelaskan asal-usul data yang dipakai di skripsi, yaitu data survei kesehatan resmi Amerika Serikat (CDC/NCHS NHANES) siklus Agustus 2021 – Agustus 2023, serta batasan klaim generalisasinya.

### B. Kenapa dilakukan?
Awalnya riset ini dirancang menggunakan data mikro Survei Kesehatan Indonesia (SKI 2023) dari Kementerian Kesehatan RI. Namun, karena data mikro SKI 2023 belum bisa diakses secara publik/resmi untuk mahasiswa saat riset berlangsung, kita bermigrasi ke NHANES yang merupakan *gold standard* data terbuka kesehatan dunia dengan pengukuran laboratorium berstandar klinis.

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Loh, kamu kan di Indonesia, kenapa pakai data Amerika (NHANES)?"*
* **Jawaban Felik:**
  > *"Betul, Pak/Bu. Awalnya riset ini dirancang untuk data mikro SKI 2023. Namun karena keterbatasan aksesibilitas data mikro SKI perorangan, kami beralih ke NHANES 2021–2023 yang berstatus open-access dan memiliki pemeriksaan laboratorium standar emas (HPLC HbA1c).*
  > *Fokus metodologis skripsi saya adalah **menguji efektivitas algoritma skrining bertingkat (two-stage non-laboratory screening) dan pemodelan non-linear (GAM)** dalam mendeteksi disglikemia yang belum terdiagnosis.*
  > *Kami secara tegas **tidak mengklaim ekstrapolasi langsung ke populasi Indonesia** maupun representasi nasional AS, melainkan membuktikan validitas mekanistik skrining non-laboratorium pada kohort epidemiologi terstandar."*

### D. Kesalahan pemahaman yang harus dihindari
* **JANGAN PERNAH BILANG:** *"Data Amerika sama saja kok dengan data Indonesia."* (Ini salah fatal, karena demografi, gaya hidup, dan batas cut-off BMI ras berbeda).
* **JANGAN BILANG:** *"Hasil akurasi model saya mewakili prevalensi seluruh rakyat Amerika."* (Tidak boleh, karena evaluasi ML kita unweighted).

---

## SECTION 2 & 3: LOAD 8 KOMPONEN XPT & NORMALISASI SAS ZERO

### A. Ini ngapain?
Membaca 8 file `.xpt` dari CDC (`DEMO_L`, `BMX_L`, `BPQ_L`, `SMQ_L`, `PAQ_L`, `DIQ_L`, `GHB_L`, `GLU_L`) dan menjalankan fungsi `normalize_sas_zeros()`.

### B. Kenapa dilakukan?
Format biner SAS (`.xpt`) saat dibaca ke Python sering mengalami masalah *floating-point underflow*, di mana angka 0 sesungguhnya dibaca komputer sebagai angka desimal yang sangat kecil (misal $5.39 \times 10^{-79}$). Kalau tidak dinormalkan ke `0.0`, perintah logika seperti `WTSAF2YR > 0` akan salah membaca orang yang bobotnya 0 sebagai "valid".

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Kenapa kamu pakai sampai 8 file terpisah? Kenapa tidak download 1 file utuh saja?"*
* **Jawaban Felik:**
  > *"Di NHANES, data dirilis secara modular oleh CDC per divisi pemeriksaan: data kuesioner wawancara rumah (`DEMO_L`, `BPQ_L`, `SMQ_L`, `PAQ_L`, `DIQ_L`), pemeriksaan fisik di klinik berjalan/MEC (`BMX_L`), dan pemeriksaan lab darah (`GHB_L`, `GLU_L`). Tidak ada file tunggal gabungan dari CDC; peneliti harus menggabungkannya sendiri secara modular."*

---

## SECTION 4: MERGE MENGGUNAKAN SEQN

### A. Ini ngapain?
Menggabungkan ke-8 tabel data peserta menggunakan primary key `SEQN` (Respondent Sequence Number) dengan metode `left join` bertumpu pada `DEMO_L` ($N = 11.933$).

### B. Kenapa dilakukan?
`SEQN` adalah ID unik peserta di seluruh NHANES. Kita memakai `left join` dari `DEMO_L` agar seluruh peserta yang diwawancarai tetap terlacak dalam tabel alur seleksi (*attrition flowchart*), sehingga tidak ada peserta yang hilang secara gaib.

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Bagaimana kamu memastikan tidak ada data yang tertukar saat merge?"*
* **Jawaban Felik:**
  > *"Kami memastikan kolom `SEQN` unik 100% (satu baris per orang), menghapus kolom tumpang tindih non-SEQN sebelum merge untuk mencegah duplikasi kolom, dan memverifikasi jumlah baris akhir tetap tepat 11.933."*

---

## SECTION 5: POPULASI KOHORT E (EXCLUDE KNOWN DIABETES & PREDIABETES)

### A. Ini ngapain?
Menyaring peserta menjadi **Kohort E**:
1. Dewasa: Umur $\ge 18$ tahun (`RIDAGEYR >= 18`).
2. Tidak pernah didiagnosis diabetes: `DIQ010 == 2` (No).
3. Tidak pernah didiagnosis prediabetes: `DIQ160 == 2` (No).
Hasilnya: $N = 5.907$ orang.

### B. Kenapa dilakukan?
Ini adalah **kunci konsep terpenting seluruh skripsi Felik**.
Tujuan alat skrining komunitas adalah menemukan **orang yang merasa dirinya sehat padahal gula darahnya sudah rusak (unrecognized dysglycemia)**.
Kalau orang yang sudah tahu dirinya diabetes atau prediabetes dimasukkan ke dalam model:
1. Mereka sudah minum obat, diet, atau kontrol dokter, sehingga perilakunya berbeda.
2. Model ML akan mengalami bias seleksi yang menipu (akurasi tampak tinggi semu karena memprediksi orang yang memang sudah terdiagnosis).
3. Skrining tidak ada gunanya untuk orang yang sudah terdiagnosis.

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Kenapa orang yang punya diabetes kamu buang? Bukannya model prediksi diabetes harus belajar dari orang diabetes?"*
* **Jawaban Felik:**
  > *"Justru itulah bedanya **Skrining Kasus Baru (Screening for Unrecognized Disease)** dengan studi faktor risiko biasa, Pak/Bu.*
  > *Di dunia nyata, skrining non-laboratorium ditujukan kepada masyarakat awam yang belum terdiagnosis. Orang yang sudah tahu dirinya diabetes (`DIQ010=1`) sudah berada di bawah perawatan dokter dan tidak butuh alat skrining tahap pertama.*
  > *Dengan hanya memasukkan Kohort E, target model kita adalah mendeteksi orang yang **secara klinis belum sadar dirinya sakit**, tetapi hasil tes darah laboratoriumnya (HbA1c) sudah masuk rentang prediabetes atau diabetes."*

### D. Kesalahan pemahaman yang harus dihindari
* Kalau peserta menjawab `7` (Refused / Menolak menjawab) atau `9` (Don't Know / Tidak tahu), **JANGAN** dianggap "No". Di kode kita, hanya yang menjawab persis `2` (No) yang masuk.

---

## SECTION 6: MEMBUAT TARGET UTAMA (HBA1C-DEFINED DYSGLYCEMIA)

### A. Ini ngapain?
Mengambil hasil lab darah HbA1c (`LBXGH`) dan membuat variabel biner:
* `hba1c_dysglycemia = 0`: Normal ($\text{HbA1c} < 5.7\%$)
* `hba1c_dysglycemia = 1`: Disglikemia ($\text{HbA1c} \ge 5.7\%$)
Di Kohort E yang punya data lab valid ($N = 4.260$):
* Normal: $3.277$ orang ($76.9\%$)
* Disglikemia: $983$ orang ($23.1\%$)

### B. Kenapa dilakukan?
Berdasarkan pedoman *American Diabetes Association* (ADA):
* $< 5.7\%$: Normal
* $5.7\% - 6.4\%$: Prediabetes
* $\ge 6.5\%$: Diabetes
Di tahap skrining awal non-laboratorium, prediabetes dan diabetes digabung menjadi satu target ("Disglikemia"), karena siapa pun yang $\ge 5.7\%$ wajib dirujuk ke faskes untuk tes darah konfirmasi (Stage 2).

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Kenapa kamu sebut 'disglikemia', kenapa bukan langsung sebut diabetes saja?"*
* **Jawaban Felik:**
  > *"Karena rentang $\ge 5.7\%$ mencakup prediabetes ($5.7\%–6.4\%$) dan undiagnosed diabetes ($\ge 6.5\%$), Pak/Bu.*
  > *Tujuan intervensi preventif faskes primer justru adalah menangkap fase prediabetes sedini mungkin sebelum berkembang menjadi komplikasi diabetes permanen. Oleh karena itu, terminologi klinis yang tepat adalah 'disglikemia berbasis HbA1c'."*
* **Dosen:** *"Apakah model kamu mendiagnosis pasien?"*
* **Jawaban Felik:**
  > *"Sama sekali tidak, Pak/Bu. Model kami adalah **alat stratifikasi risiko non-laboratorium Tahap 1**. Pasien yang dinyatakan berisiko tinggi (screen-positive) tetap harus dirujuk ke laboratorium untuk pemeriksaan darah definitif (Tahap 2)."*

---

## SECTION 7 & 8: REKAYASA PREDIKTOR & MEMBERSIHKAN KODE KHUSUS (PAD680)

### A. Ini ngapain?
Membersihkan dan mengodekan variabel fitur non-laboratorium:
1. `age` (18–80 tahun)
2. `sex` (1 = Laki-laki, 2 = Perempuan)
3. `bmi` ($\text{kg/m}^2$)
4. `hypertension_history` (1 = Ya, 2 = Tidak; 7 & 9 jadi NaN)
5. `smoking_history` (1 = Pernah merokok $\ge 100$ batang seumur hidup, 2 = Tidak; 7 & 9 jadi NaN)
6. `waist_cm` (Lingkar pinggang dalam cm)
7. `sedentary_minutes_day` (Menit duduk per hari dari `PAD680`)

### B. Kenapa dilakukan? (Kasus Khusus PAD680)
Pada kuesioner aktivitas fisik `PAD680`:
* Nilai asli dari kuesioner jika orang menolak menjawab adalah `7777` (*Refused*).
* Nilai jika orang tidak tahu / lupa adalah `9999` (*Don't Know*).
* **Masalah Audit:** Di tahap awal (eksplorasi V2), pengecekan missing value hanya memakai `.notna()`. Akibatnya, angka `9999` dianggap sebagai angka valid duduk selama $9.999$ menit/hari ($166,65$ jam sehari!).
* Di Phase 3, angka `7777` dan `9999` wajib di-replace menjadi `np.nan`. Ini menjelaskan persis kenapa jumlah sampel lengkap turun dari $4.066$ ke $4.044$ (ada 22 orang yang menjawab 9999 atau 7777).

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Kenapa jumlah sampel expanded kamu berubah dari 4.066 menjadi 4.044? Kamu sengaja hapus 22 orang supaya akurasi bagus ya?"*
* **Jawaban Felik:**
  > *"Tidak sama sekali, Pak/Bu. Penurunan 22 orang itu adalah **koreksi integritas data (data-quality correction)**.*
  > *Pada kuesioner CDC `PAD680`, kode `9999` artinya 'Don't Know' dan `7777` artinya 'Refused'. Jika tidak diubah ke missing (NaN), komputer akan mengira orang tersebut duduk $166$ jam dalam satu hari, yang mustahil secara biologis dan merusak skala normalisasi model.*
  > *Ada persis 21 orang menjawab 9999 dan 1 orang menjawab 7777. Mengubah keduanya menjadi NaN adalah langkah standar pengolahan data survei resmi CDC."*

---

## SECTION 9 & 10: CORE VS EXPANDED DATASET & PENCEGAHAN LEAKAGE

### A. Ini ngapain?
Membagi prediktor menjadi 2 set fitur:
1. **Core Predictors (5 fitur):** `age, sex, bmi, hypertension_history, smoking_history`.
2. **Expanded Predictors (7 fitur):** Core + `waist_cm` + `sedentary_minutes_day`.
Dan membuat pagar pengaman (*Leakage Guard*) agar variabel terlarang tidak masuk ke matriks $X$.

### B. Kenapa dilakukan?
* **Core** dirancang untuk skrining dengan beban instrumen paling minimal (tanpa perlu meteran lingkar pinggang dan kuesioner duduk yang panjang).
* **Expanded** menguji apakah penambahan lingkar pinggang dan durasi duduk mampu meningkatkan performa diskriminasi.
* **Leakage Guard:** Mencegah kebocoran data. Variabel lab (`LBXGH`, `LBXGLU`), variabel definisi kohort (`DIQ010`, `DIQ160`), dan bobot survei (`WTPH2YR`, `SDMVSTRA`) mutlak dilarang masuk ke $X$.

### C. Kalau dosen nanya, jawab apa?
* **Dosen:** *"Kenapa bobot survei (survey weights) tidak kamu jadikan fitur di model Machine Learning?"*
* **Jawaban Felik:**
  > *"Karena bobot survei (`WTPH2YR`, `SDMVSTRA`, `SDMVPSU`) adalah probabilitas sampling desain survei CDC untuk mengestimasi statistik agregat populasi AS.*
  > *Bobot survei bukan karakteristik klinis atau biologis pasien. Jika seorang pasien datang ke posyandu di dunia nyata, dokter tidak memiliki bobot survei pasien tersebut. Memasukkan bobot survei sebagai fitur prediksi akan menimbulkan data leakage dan bias operasional."*

---

## SECTION 11 & 12: VALIDASI REPRODUSIBILITAS & RANGKUMAN ANGKA

### Tabel Attrisi Pasien (Wajib Hafal di Luar Kepala!)

| Tahapan Seleksi | Kriteria | Jumlah Pasien ($N$) | Catatan |
|:---|:---|---:|:---|
| **1. Total NHANES** | Seluruh responden survei 2021–2023 | **11.933** | Base merge `DEMO_L` |
| **2. Populasi Dewasa** | Umur $\ge 18$ tahun | **8.153** | Eksklusi anak-anak |
| **3. Kohort E** | Tanpa riwayat diabetes & prediabetes | **5.907** | Target skrining unrecognized |
| **4. Valid HbA1c** | Punya hasil lab darah HbA1c valid | **4.260** | Normal: $3.277$, Disglikemia: $983$ |
| **5. Core Complete** | Lengkap 5 prediktor Core | **4.194** | Normal: $3.224$, Disglikemia: $970$ |
| **6. Expanded Complete**| Lengkap 7 prediktor Expanded | **4.044** | Normal: $3.106$, Disglikemia: $938$ |

*Prevalensi disglikemia di populasi skrining adalah $\approx 23.19\%$.*

---

## RINGKASAN MENTAL FELIK SAAT SIDANG

1. **Topik Riset:** Skrining bertingkat non-laboratorium untuk mendeteksi disglikemia tersembunyi.
2. **Bukan Diagnosa:** Model memfilter orang berisiko tinggi untuk dirujuk ke tes HbA1c.
3. **Bukan Future Prediction:** Model mendeteksi kondisi disglikemia yang *saat ini sudah ada tapi belum disadari*.
4. **Data:** NHANES 2021–2023, Kohort E ($N = 4.044$ kasus lengkap), prevalensi $23.19\%$.
5. **Kualitas Metodologis:** Tidak ada kebocoran data (zero leakage), kode missing 9999 dibersihkan secara benar, dan hasil data reproduksibel 100% dengan data Phase 3.
