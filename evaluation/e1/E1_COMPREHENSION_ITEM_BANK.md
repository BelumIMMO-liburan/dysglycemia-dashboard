# Objective Comprehension Item Bank (Phase E1)
## Protocol-Defined Objective Comprehension Battery (8 Items)

**Document Identifier:** `E1-COMP-ITEM-BANK-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Item Bank Design & Psychometric Governance

To objectively quantify participant comprehension of system mechanics (RQ4) without relying on subjective self-reporting, this battery establishes **eight objective multiple-choice items**.

- **Construct Status:** **Objective / Protocol-Defined Battery**. *(Pre-pilot psychometric testing does not by itself establish full formal psychometric validation; therefore the label "Validated" is explicitly eschewed in favor of "Objective Protocol-Defined")*.
- **Structure:** 4 options per question (1 keyed correct answer, 3 plausible distractors).
- **Scoring:** Binary (1 = Correct, 0 = Incorrect). Composite score range: $0 \le S \le 8$.
- **Required Item Enforcement:** All 8 items are designated as **MANDATORY (Required)** within the digital survey delivery platform. This design prevents accidental user omission from being penalized as incorrect conceptual understanding. Technical dropouts or unsubmitted surveys are handled under the formal missing-data protocol.
- **Language Alignment:** Formally administered in **Bahasa Indonesia** for Indonesian participants, alongside official English reference text.

---

## 2. Complete 8-Item Battery (English Source & Indonesian Administration)

### ITEM 1 (Domain A: Screening vs. Diagnosis Meaning)
**Item Code:** `COMP_01`  
- **English Question:** When the dashboard reports an "Elevated Screening Signal" for a synthetic screening profile, what does this result mean?  
  - **[A]** The individual has been diagnosed with diabetes by the system.  
  - **[B]** The statistical screening model estimated a probability above the referral threshold, recommending Stage-2 HbA1c laboratory assessment. *(Keyed Correct)*  
  - **[C]** The individual is guaranteed to develop diabetes complications within the next year.  
  - **[D]** The laboratory has confirmed elevated blood glucose.  
- **Bahasa Indonesia Translation:** Ketika dashboard menampilkan "Elevated Screening Signal" (Sinyal Skrining Meningkat) untuk sebuah profil skrining sintetis, apakah arti dari hasil tersebut?  
  - **[A]** Individu tersebut telah didiagnosis menderita diabetes oleh sistem.  
  - **[B]** Model skrining statistik memperkirakan probabilitas di atas ambang batas rujukan, merekomendasikan penilaian laboratorium HbA1c Tahap-2. *(Kunci Benar)*  
  - **[C]** Individu tersebut dipastikan akan mengalami komplikasi diabetes dalam satu tahun ke depan.  
  - **[D]** Laboratorium telah mengonfirmasi peningkatan kadar glukosa darah.  
- **Keyed Correct:** **[B]**  
- **Conceptual Rationale:** Tests understanding that Stage-1 non-laboratory screening is a statistical triage signal, not a medical diagnosis.

---

### ITEM 2 (Domain B: Lower Screening Signal Interpretation)
**Item Code:** `COMP_02`  
- **English Question:** If a synthetic screening profile receives a "Lower Screening Signal" (AI recommendation: No Referral), what does this indicate?  
  - **[A]** The individual is completely free of diabetes and will never require future screening.  
  - **[B]** The individual's estimated screening probability was below the decision threshold, so secondary laboratory assessment is not currently flagged. *(Keyed Correct)*  
  - **[C]** The laboratory blood test showed completely normal glucose levels.  
  - **[D]** The individual has 0.0% biological probability of dysglycemia.  
- **Bahasa Indonesia Translation:** Jika sebuah profil skrining sintetis menerima "Lower Screening Signal" (Sinyal Skrining Lebih Rendah / Rekomendasi AI: Tidak Perlu Rujukan), apakah artinya?  
  - **[A]** Individu tersebut sepenuhnya bebas diabetes dan tidak akan pernah memerlukan skrining lagi.  
  - **[B]** Estimasi probabilitas skrining individu berada di bawah ambang keputusan, sehingga rujukan laboratorium lanjutan saat ini tidak direkomendasikan. *(Kunci Benar)*  
  - **[C]** Pemeriksaan darah laboratorium menunjukkan kadar glukosa yang sepenuhnya normal.  
  - **[D]** Individu tersebut memiliki probabilitas biologis 0,0% terhadap disglikemia.  
- **Keyed Correct:** **[B]**  
- **Conceptual Rationale:** Tests understanding that a lower signal does not rule out disease or guarantee zero risk, but merely falls below the operating cutoff.

---

### ITEM 3 (Domain C: Explainability Factor Direction)
**Item Code:** `COMP_03`  
- **English Question:** In the "Why this result?" section, what does it mean when a factor (such as Age) is listed under "Pushes screening score higher"?  
  - **[A]** That this input factor mathematically increased the statistical model's calculated screening score in the additive calculation. *(Keyed Correct)*  
  - **[B]** That this factor was medically proven to cause diabetes in this individual.  
  - **[C]** That the individual must immediately undergo medical intervention for that factor.  
  - **[D]** That this was the only factor considered by the computer model.  
- **Bahasa Indonesia Translation:** Pada bagian "Why this result?" (Mengapa hasil ini?), apakah artinya jika sebuah faktor (seperti Usia) terdaftar di bawah "Pushes screening score higher" (Mendorong skor skrining lebih tinggi)?  
  - **[A]** Bahwa faktor input tersebut secara matematis meningkatkan skor skrining terhitung model statistik dalam perhitungan aditif. *(Kunci Benar)*  
  - **[B]** Bahwa faktor tersebut terbukti secara medis menyebabkan diabetes pada individu ini.  
  - **[C]** Bahwa individu tersebut harus segera menjalani tindakan medis terkait faktor tersebut.  
  - **[D]** Bahwa faktor tersebut adalah satu-satunya faktor yang diperhitungkan oleh model komputer.  
- **Keyed Correct:** **[A]**  
- **Conceptual Rationale:** Tests understanding of additive feature attribution directionality without relying on undefined "baseline contribution" jargon.

---

### ITEM 4 (Domain D: Explainability Causality Boundary)
**Item Code:** `COMP_04`  
- **English Question:** Does the factor explanation chart prove that a specific model input factor caused the individual's metabolic condition?  
  - **[A]** Yes, because machine learning models identify true biological causes.  
  - **[B]** Yes, if the factor appears at the very top of the ranking.  
  - **[C]** No; the chart displays statistical model associations and additive contributions, not clinical proof of biological cause and effect. *(Keyed Correct)*  
  - **[D]** Yes, because the data were sourced from national health statistics.  
- **Bahasa Indonesia Translation:** Apakah grafik penjelasan faktor membuktikan bahwa suatu faktor input model tertentu menyebabkan kondisi metabolik individu tersebut?  
  - **[A]** Ya, karena model machine learning menemukan penyebab biologis yang sebenarnya.  
  - **[B]** Ya, jika faktor tersebut berada di posisi teratas dalam peringkat.  
  - **[C]** Tidak; grafik tersebut menampilkan asosiasi statistik dan kontribusi aditif model, bukan bukti klinis sebab-akibat biologis. *(Kunci Benar)*  
  - **[D]** Ya, karena data bersumber dari survei statistik kesehatan nasional.  
- **Keyed Correct:** **[C]**  
- **Conceptual Rationale:** Tests resistance to the Explanation-Causality Fallacy.

---

### ITEM 5 (Domain E: Human Override Semantics)
**Item Code:** `COMP_05`  
- **English Question:** When a reviewer performs a "Human Override" from "No Referral" to "Refer", what actually changes in the system?  
  - **[A]** The statistical model recalculates and increases the calculated AI probability.  
  - **[B]** The final human referral decision is updated, while the original AI calculation remains unchanged in the audit record. *(Keyed Correct)*  
  - **[C]** The individual's biological blood sugar levels are altered.  
  - **[D]** The underlying machine learning model is permanently retrained with the new decision.  
- **Bahasa Indonesia Translation:** Ketika seorang peninjau melakukan "Human Override" (Pengesampingan Manusia) dari "No Referral" menjadi "Refer", apa yang sebenarnya berubah di dalam sistem?  
  - **[A]** Model statistik menghitung ulang dan menaikkan nilai probabilitas AI.  
  - **[B]** Keputusan akhir rujukan manusia diperbarui, sedangkan perhitungan asli AI tetap tersimpan tanpa perubahan dalam catatan audit. *(Kunci Benar)*  
  - **[C]** Kadar gula darah biologis individu tersebut berubah.  
  - **[D]** Model machine learning di belakang sistem dilatih ulang secara permanen dengan keputusan baru tersebut.  
- **Keyed Correct:** **[B]**  
- **Conceptual Rationale:** Tests understanding that Human Override changes the downstream administrative referral action, preserving machine provenance.

---

### ITEM 6 (Domain F: Stage-2 Laboratory Range Meaning)
**Item Code:** `COMP_06`  
- **English Question:** When an HbA1c value of 6.6% is entered in Stage 2 and displays "Diabetes range", what is the status of this output?  
  - **[A]** It is an automatic, legally binding medical diagnosis issued by the prototype.  
  - **[B]** It displays HbA1c laboratory-range categorization based on the protocol's cited criteria (ADA guidelines), requiring clinical interpretation. *(Keyed Correct)*  
  - **[C]** It is an AI prediction generated by a neural network.  
  - **[D]** It indicates that the Stage-1 model was 100% correct.  
- **Bahasa Indonesia Translation:** Ketika nilai HbA1c 6,6% dimasukkan pada Tahap 2 dan menampilkan "Diabetes range" (Rentang diabetes), apakah status dari hasil keluaran ini?  
  - **[A]** Ini adalah diagnosis medis otomatis dan mengikat secara hukum yang diterbitkan oleh prototipe.  
  - **[B]** Ini menampilkan kategorisasi rentang laboratorium HbA1c berdasarkan kriteria acuan protokol (panduan standar ADA), yang tetap memerlukan interpretasi klinis. *(Kunci Benar)*  
  - **[C]** Ini adalah prediksi AI baru yang dihasilkan oleh jaringan saraf tiruan (neural network).  
  - **[D]** Ini menandakan bahwa model Tahap-1 benar 100%.  
- **Keyed Correct:** **[B]**  
- **Conceptual Rationale:** Tests understanding that Stage-2 displays standard clinical laboratory thresholds, not automated computer diagnoses.

---

### ITEM 7 (Domain G: Machine Provenance & Audit Trail Permanence)
**Item Code:** `COMP_07`  
- **English Question:** After a Human Reviewer overrides an AI recommendation and saves the record, what happens to the original machine recommendation in the case history?  
  - **[A]** It is permanently deleted to avoid confusion.  
  - **[B]** It is overwritten and replaced by the human reviewer's choice.  
  - **[C]** It remains permanently recorded and visible in the audit trail alongside the override reason and reviewer code. *(Keyed Correct)*  
  - **[D]** It is hidden and accessible only to database administrators.  
- **Bahasa Indonesia Translation:** Setelah Peninjau Manusia mengesampingkan (override) rekomendasi AI dan menyimpan data, apa yang terjadi pada rekomendasi awal mesin di riwayat kasus?  
  - **[A]** Dihapus secara permanen agar tidak membingungkan.  
  - **[B]** Ditimpa dan digantikan oleh pilihan peninjau manusia.  
  - **[C]** Tetap tercatat secara permanen dan terlihat dalam jejak audit bersama dengan alasan override dan kode peninjau. *(Kunci Benar)*  
  - **[D]** Disembunyikan dan hanya dapat diakses oleh administrator basis data.  
- **Keyed Correct:** **[C]**  
- **Conceptual Rationale:** Tests awareness of immutable auditability and dual-provenance transparency.

---

### ITEM 8 (Domain H: Human–AI Concordance vs. Clinical Truth)
**Item Code:** `COMP_08`  
- **English Question:** When research analytics report an 85% "Human–AI Agreement Rate", what does this percentage represent?  
  - **[A]** That the AI model made the clinically correct medical diagnosis in 85% of cases.  
  - **[B]** That the human reviewer agreed with the AI referral recommendation in 85% of reviewed screenings. *(Keyed Correct)*  
  - **[C]** That the model's clinical sensitivity is exactly 85%.  
  - **[D]** That 85% of screened individuals in the database had confirmed diabetes.  
- **Bahasa Indonesia Translation:** Ketika analitik riset melaporkan "Human–AI Agreement Rate" (Tingkat Kesepakatan Manusia-AI) sebesar 85%, apakah arti dari persentase tersebut?  
  - **[A]** Bahwa model AI membuat diagnosis medis yang benar secara klinis pada 85% kasus.  
  - **[B]** Bahwa peninjau manusia menyetujui rekomendasi rujukan AI pada 85% skrining yang ditinjau. *(Kunci Benar)*  
  - **[C]** Bahwa sensitivitas klinis model tepat bernilai 85%.  
  - **[D]** Bahwa 85% individu yang diskrining dalam basis data terkonfirmasi menderita diabetes.  
- **Keyed Correct:** **[B]**  
- **Conceptual Rationale:** Tests resistance to the Agreement-as-Accuracy Fallacy.
