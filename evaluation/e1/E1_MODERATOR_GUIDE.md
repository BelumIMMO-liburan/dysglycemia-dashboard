# Standardized Moderator Guide & Script (Phase E1)
## Facilitator Instructions, Orientation Script & Assistance Hierarchy

**Document Identifier:** `E1-MODERATOR-GUIDE-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  
**Primary Study Language:** **Bahasa Indonesia** (with English documentation reference)  
**Canonical Stimulus Authority:** [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md)  

---

## 1. Facilitator Role & Neutrality Principles

The moderator's primary duty is to ensure **standardized, objective experimental conditions** across all study sessions.

### Three Unbreakable Facilitator Rules:
1. **Verbatim Fidelity:**  
   The moderator must adhere strictly to the orientation and task scripts. Spontaneous explanations of machine learning concepts or medical definitions are forbidden.
2. **Strict Epistemic Boundary in Orientation:**  
   The moderator explains **HOW** to interact with the UI elements (buttons, inputs, accordions). The moderator **NEVER EXPLAINS THE ANSWERS TO COMPREHENSION ITEMS** (e.g., never explain that an elevated signal is not a diagnosis, or why smoking affects risk).
3. **Impartial Observation:**  
   Do not praise or criticize participant actions. Maintain a calm, neutral demeanor regardless of participant errors or task completion speed.

> [!IMPORTANT]
> **Pilot / Ethics Sequencing Notice:**  
> Designation as `READY FOR PILOT REVIEW` does NOT authorize participant contact. Pilot execution may begin only after applicable supervisor and institutional ethics requirements for pilot participant involvement have been satisfied. If institutional ethics approval is required before pilot data collection, obtain it first.

---

## 2. Pre-Session Setup Checklist

Before welcoming each participant:
- [ ] Verify prototype server is running against clean `db_study.sqlite3` (`py -3.10 manage.py runserver`).
- [ ] Open Google Chrome or Mozilla Firefox to `http://127.0.0.1:8000/`.
- [ ] Verify browser window is set to $100\%$ zoom with full desktop resolution ($\ge 1280 \times 800$).
- [ ] Open developer console to ensure zero JavaScript errors on the initial page.
- [ ] Prepare physical or digital Participant Code card (e.g., `P012`).
- [ ] Prepare physical Case Scenario Cards (`CASE-ALPHA` and `CASE-BETA`) strictly matching [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md).
- [ ] Prepare external questionnaire link pre-filled with the participant's code.
- [ ] Prepare Moderator Observation Sheet to log timestamps, errors, and assistance levels.

---

## 3. Step-by-Step Scripted Session Walkthrough

### PHASE 1: Greeting, Purpose & Informed Consent (Approx. 5 Mins)

**Bahasa Indonesia Script (Administered):**
> *"Halo dan terima kasih telah bersedia berpartisipasi dalam sesi evaluasi hari ini. Nama saya [Nama Peneliti], dan saya melaksanakan penelitian ini untuk skripsi sarjana ilmu komputer saya.*
>
> *Hari ini, Anda akan berinteraksi dengan prototipe riset aplikasi web yang dirancang untuk skrining diabetes dua tahap. Aplikasi ini menggunakan model statistik machine learning untuk memperkirakan apakah seseorang perlu dirujuk untuk penilaian laboratorium HbA1c Tahap-2, menyajikan visualisasi faktor penjelasan, dan memungkinkan peninjau manusia untuk memeriksa serta memfinalisasi keputusan rujukan.*
>
> *Sebelum kita mulai, saya ingin menegaskan beberapa poin penting:*
> 1. *Kita sedang menguji antarmuka perangkat lunak, kejelasan alur kerja, dan tata letak. Kita TIDAK sedang menguji kemampuan Anda, kecerdasan Anda, ataupun pengetahuan medis pribadi Anda.*
> 2. *Aplikasi ini adalah prototipe akademis ilmu komputer. Ini bukan perangkat medis tersertifikasi dan tidak memberikan diagnosis medis formal.*
> 3. *Seluruh tugas akan menggunakan profil skrining fiktif/sintetis. Anda tidak akan pernah diminta memasukkan data kesehatan pribadi Anda.*
> 4. *Partisipasi Anda sepenuhnya bersifat sukarela, dan seluruh respons akan dijaga kerahasiaannya di bawah kode partisipan anonim.*
>
> *Silakan membaca Lembar Informasi dan Persetujuan ini. Jika Anda menyetujui, silakan menandatanganinya di bagian bawah."*

**English Reference Translation:**
> *"Hello and thank you for taking part in this evaluation session today. My name is [Researcher Name], and I am conducting this study for my undergraduate computer science thesis. Today, you will be interacting with a research prototype web application designed for two-stage diabetes screening... We are testing the software interface, layout, and workflow clarity. We are NOT testing you... All tasks will use fictitious, synthetic screening profiles... If you agree, please sign at the bottom."*

*[Participant reviews and signs consent form. Moderator hands participant their unique study code card: e.g., `P012`].*

---

## PHASE 2: Neutral Interface Orientation (Approx. 5 Mins)

**Bahasa Indonesia Script (Administered):**
> *"Terima kasih. Sekarang, saya akan memberikan gambaran umum yang netral mengenai tata letak antarmuka. Silakan melihat ke layar.*
>
> *Di sisi kiri, Anda melihat bilah navigasi dengan menu 'New Screening', 'Review Queue', 'History', 'Analytics', dan 'About the Model'.*
>
> *Area tengah menampilkan ruang kerja aktif. Sepanjang tugas, Anda akan melihat formulir web standar, tabel data, kartu informasi, dan tombol aksi.*
>
> *Selama sesi berlangsung, saya akan memberikan kartu skenario tugas berisi petunjuk spesifik dan data sintetis. Silakan baca setiap instruksi dengan saksama dan kerjakan sesuai kenyamanan Anda. Jika muncul pesan validasi atau jendela modal, berinteraksilah seperti biasanya Anda menggunakan situs web.*
>
> *Apakah ada pertanyaan sebelum kita memulai Tugas 1?"*

*[Moderator answers general procedural questions only. Does not explain clinical terms or model features].*

---

### PHASE 3: Task Execution (Tasks 1 through 6) (Approx. 15–20 Mins)

The moderator presents the scenario cards one by one:
- **Task 1 Card:** Hands `CASE-ALPHA` card. *"Silakan ikuti instruksi pada Kartu Tugas 1."* (Participant inputs 7 values, clicks `Review Inputs`, then clicks `Run Screening`).
- **Task 2 Card:** Hands `Task 2` card. *"Silakan periksa hasil skrining dan penjelasan faktor pada bagian 'Why this result?' sesuai petunjuk Kartu Tugas 2."* (Participant clicks `Show all 7 factors`, identifies Age as elevating and Sedentary/Waist/Smoking/Male sex as moderating).
- **Task 3 Card:** Hands `Task 3` card. *"Silakan lanjutkan ke Kartu Tugas 3 untuk memfinalisasi peninjauan manusia."* (Participant enters code into `Reviewer Code` field, clicks `Accept Recommendation`).
- **Task 4 Card:** Hands `CASE-BETA` card and `Task 4` card. *"Silakan masukkan data Kasus Beta dan lakukan alur pengesampingan (override) sesuai petunjuk Kartu Tugas 4."* (Participant enters inputs, opens override dialog, enters code, selects reason `Referral is preferred as a precaution`, enters note, clicks `Confirm Override`).
- **Task 5 Card:** Hands `Task 5` card. *"Silakan kembali ke Kasus Alpha, klik 'Proceed to Stage-2 HbA1c Assessment', dan masukkan data uji laboratorium sesuai Kartu Tugas 5."* (Participant enters 6.1%, clicks `Review HbA1c Value`, clicks `Confirm Laboratory Result`).
- **Task 6 Card:** Hands `Task 6` card. *"Silakan buka menu 'History', cari baris Kasus Beta, klik 'View Case', dan periksa jejak audit sesuai petunjuk Kartu Tugas 6."* (Participant verifies original AI recommendation was permanently preserved).

#### Applying the 4-Level Assistance Protocol:
1. **Level 0 (No Help):** Participant works independently. Moderator takes notes silently.
2. **Level 1 (General Prompt):**  
   *Trigger:* Participant pauses for $>30$ seconds or looks at moderator for help.  
   *Script:* *"Silakan lanjutkan menggunakan informasi dan tombol yang tersedia di layar."*
3. **Level 2 (Directional Hint):**  
   *Trigger:* Participant remains blocked for an additional $>30$ seconds or navigates away from the task area.  
   *Script:* *"Perhatikan kartu di bagian tengah halaman."* or *"Lihat pilihan aksi pada panel peninjauan di bagian bawah."*
4. **Level 3 (Procedural Demonstration):**  
   *Trigger:* Participant expresses severe frustration, cannot locate the required control after 2 minutes, or attempts an invalid action that would terminate the session.  
   *Script:* *"Biar saya tunjukkan di mana tombol tersebut berada."* [Moderator points to or clicks the control].  
   *Logging Rule:* Mark `task_success = 0` and log `assist_level = 3`.

---

### PHASE 4: Post-Task Survey Battery (Approx. 10–15 Mins)

**Bahasa Indonesia Script (Administered):**
> *"Terima kasih telah menyelesaikan seluruh tugas. Sekarang, mohon mengisi kuesioner evaluasi akhir pada formulir digital di komputer ini.*
>
> *Kuesioner ini terdiri atas empat bagian:*
> 1. *Kuis pemahaman objektif 8 pertanyaan mengenai arti hasil dan mekanisme sistem.*
> 2. *Kuesioner System Usability Scale (SUS) adaptasi bahasa Indonesia (10 pertanyaan).*
> 3. *Lima pernyataan mengenai kejelasan antarmuka dan kendali sistem.*
> 4. *Tiga pertanyaan terbuka untuk masukan atau kendala yang Anda rasakan.*
>
> *Seluruh pertanyaan telah diatur wajib diisi. Mohon menjawab dengan jujur sesuai pengalaman yang baru saja Anda alami. Tidak ada jawaban benar atau salah pada pertanyaan usabilitas."*

*[Participant completes external survey. Moderator verifies that Participant Code was recorded].*

---

### PHASE 5: Debriefing & Session Close (Approx. 2 Mins)

**Bahasa Indonesia Script (Administered):**
> *"Sesi evaluasi kita hari ini telah selesai. Apakah ada pertanyaan mengenai penelitian ini atau aplikasi yang Anda gunakan?*
>
> *Terima kasih banyak atas waktu dan kontribusi berharga Anda dalam penelitian skripsi ini."*

*[Moderator securely archives observation sheet and resets server/database for the next session].*
