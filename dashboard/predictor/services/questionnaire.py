"""
Dashboard Questionnaire & Evaluation Instrument Service.
Protocol E1 v1.0.3 & E2 Implementation

Defines and manages:
1. 8 Objective Comprehension Questions (C1–C8) with server-side scoring (0–8, %).
2. 10 System Usability Scale Items using the validated Indonesian adaptation by Sharfina & Santoso (2016).
3. 5 Dashboard Clarity Items (DQ1–DQ5).
4. 3 Open-Ended Feedback Questions (OQ1–OQ3).
5. Practice Case P0 Onboarding Specification.
"""

from typing import Dict, List, Tuple, Any

# ==============================================================================
# SECTION A: OBJECTIVE COMPREHENSION (8 ITEMS, CLOSED-BOOK)
# ==============================================================================

COMPREHENSION_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "C1",
        "question": "Apa yang ditunjukkan oleh nilai probabilitas pada hasil screening AI?",
        "options": {
            "A": "Kepastian bahwa seseorang mengalami diabetes",
            "B": "Perkiraan model berdasarkan data input yang diberikan",
            "C": "Hasil pemeriksaan HbA1c",
            "D": "Keputusan akhir yang wajib diikuti pengguna",
        },
        "correct_answer": "B",
    },
    {
        "id": "C2",
        "question": "Apa arti rekomendasi \"REFER\" pada Stage 1?",
        "options": {
            "A": "Sistem memastikan pengguna mengalami diabetes",
            "B": "Sistem menyarankan pemeriksaan lanjutan berdasarkan hasil screening",
            "C": "Pengguna harus langsung menjalani pengobatan",
            "D": "HbA1c pengguna sudah pasti berada di atas 6,5%",
        },
        "correct_answer": "B",
    },
    {
        "id": "C3",
        "question": "Apa tujuan feature contribution pada penjelasan AI?",
        "options": {
            "A": "Menunjukkan penyebab biologis dari kondisi pengguna",
            "B": "Menunjukkan bagaimana fitur input berkontribusi terhadap output model",
            "C": "Menggantikan hasil pemeriksaan laboratorium",
            "D": "Menentukan diagnosis akhir pengguna",
        },
        "correct_answer": "B",
    },
    {
        "id": "C4",
        "question": "Kapan Human Override terjadi?",
        "options": {
            "A": "Ketika model menghasilkan probabilitas 0%",
            "B": "Ketika pengguna mengubah data input",
            "C": "Ketika keputusan akhir manusia berbeda dari rekomendasi AI",
            "D": "Ketika pengguna melihat XAI",
        },
        "correct_answer": "C",
    },
    {
        "id": "C5",
        "question": "Jika AI memberikan rekomendasi REFER tetapi manusia memilih DO NOT REFER, bagaimana hubungan keputusan tersebut dipahami?",
        "options": {
            "A": "AI pasti melakukan kesalahan",
            "B": "Manusia pasti melakukan kesalahan",
            "C": "Terjadi ketidaksesuaian antara rekomendasi AI dan keputusan manusia",
            "D": "Sistem otomatis mengubah probabilitas AI",
        },
        "correct_answer": "C",
    },
    {
        "id": "C6",
        "question": "Apa tujuan feedback yang diberikan setelah Human Override?",
        "options": {
            "A": "Mengubah nilai HbA1c pengguna",
            "B": "Memberikan sinyal koreksi dari keputusan manusia yang dapat digunakan dalam mekanisme adaptation",
            "C": "Menghapus prediksi AI sebelumnya",
            "D": "Mengubah hasil final-test model",
        },
        "correct_answer": "B",
    },
    {
        "id": "C7",
        "question": "Kapan pemeriksaan HbA1c pada Stage 2 dilakukan dalam alur dashboard?",
        "options": {
            "A": "Selalu dilakukan setelah Stage 1",
            "B": "Hanya setelah keputusan akhir manusia adalah REFER",
            "C": "Hanya ketika AI memberikan probabilitas 100%",
            "D": "Sebelum Stage 1",
        },
        "correct_answer": "B",
    },
    {
        "id": "C8",
        "question": "Apa perbedaan utama Stage 1 dan Stage 2 pada dashboard?",
        "options": {
            "A": "Stage 1 menggunakan HbA1c, sedangkan Stage 2 menggunakan data non-laboratorium",
            "B": "Keduanya merupakan diagnosis otomatis",
            "C": "Stage 1 melakukan non-laboratory risk screening, sedangkan Stage 2 menggunakan HbA1c untuk laboratory-range assessment",
            "D": "Stage 2 digunakan untuk melatih ulang GAM-v1",
        },
        "correct_answer": "C",
    },
]

# Canonical answer keys stored strictly on server side
COMPREHENSION_ANSWER_KEYS: Dict[str, str] = {
    item["id"]: item["correct_answer"] for item in COMPREHENSION_ITEMS
}


def score_comprehension(answers: Dict[str, str]) -> Tuple[int, float]:
    """
    Score the 8 objective comprehension items on the server side.
    Each item: 1 if correct, 0 if incorrect.
    
    Returns:
        Tuple of (score: int [0..8], percentage: float [0.0..100.0])
    """
    correct_count = 0
    for item_id, correct in COMPREHENSION_ANSWER_KEYS.items():
        user_ans = str(answers.get(item_id, "")).strip().upper()
        if user_ans == correct:
            correct_count += 1

    pct = round((correct_count / len(COMPREHENSION_ANSWER_KEYS)) * 100.0, 1)
    return correct_count, pct


# ==============================================================================
# SECTION B: SYSTEM USABILITY SCALE (10 ITEMS)
# Indonesian Adaptation: Sharfina & Santoso (2016)
# ==============================================================================

SUS_ITEMS: List[Dict[str, Any]] = [
    {
        "num": 1,
        "polarity": "positive",
        "text": "Saya berpikir bahwa saya ingin sering menggunakan sistem ini.",
    },
    {
        "num": 2,
        "polarity": "negative",
        "text": "Saya merasa sistem ini rumit untuk digunakan.",
    },
    {
        "num": 3,
        "polarity": "positive",
        "text": "Saya merasa sistem ini mudah digunakan.",
    },
    {
        "num": 4,
        "polarity": "negative",
        "text": "Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini.",
    },
    {
        "num": 5,
        "polarity": "positive",
        "text": "Saya merasa fungsi-fungsi dalam sistem ini bekerja dengan baik.",
    },
    {
        "num": 6,
        "polarity": "negative",
        "text": "Saya merasa ada banyak hal yang tidak konsisten pada sistem ini.",
    },
    {
        "num": 7,
        "polarity": "positive",
        "text": "Saya merasa bahwa orang lain akan memahami cara menggunakan sistem ini dengan cepat.",
    },
    {
        "num": 8,
        "polarity": "negative",
        "text": "Saya merasa sistem ini membingungkan.",
    },
    {
        "num": 9,
        "polarity": "positive",
        "text": "Saya merasa tidak ada hambatan dalam menggunakan sistem ini.",
    },
    {
        "num": 10,
        "polarity": "negative",
        "text": "Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini.",
    },
]

SUS_SCALE_LABELS = {
    1: "Sangat Tidak Setuju",
    2: "Tidak Setuju",
    3: "Netral",
    4: "Setuju",
    5: "Sangat Setuju",
}


def score_sus(responses: Dict[int, int]) -> float:
    """
    Standard System Usability Scale (SUS) scoring (Brooke, 1996 / Sharfina & Santoso, 2016).
    
    Calculation:
    - For odd items (1, 3, 5, 7, 9): score = response - 1
    - For even items (2, 4, 6, 8, 10): score = 5 - response
    - Cumulative Score = sum(item_scores) * 2.5
    - Range: 0.0 to 100.0
    
    Returns:
        float score between 0.0 and 100.0.
    """
    if len(responses) != 10:
        raise ValueError(f"SUS scoring requires exactly 10 responses, got {len(responses)}.")

    adjusted_scores = []
    for k in range(1, 11):
        val = int(responses[k])
        if not (1 <= val <= 5):
            raise ValueError(f"SUS response for item {k} must be in [1, 5], got {val}.")
        
        if k % 2 == 1:
            adjusted = val - 1
        else:
            adjusted = 5 - val
        adjusted_scores.append(adjusted)

    total_sus = sum(adjusted_scores) * 2.5
    return round(total_sus, 2)


# ==============================================================================
# SECTION C: DASHBOARD CLARITY (5 ITEMS, ANALYZED INDIVIDUALLY)
# ==============================================================================

CLARITY_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "DQ1",
        "text": "Informasi yang ditampilkan pada dashboard mudah saya pahami.",
    },
    {
        "id": "DQ2",
        "text": "Penjelasan feature contribution membantu saya memahami hasil AI.",
    },
    {
        "id": "DQ3",
        "text": "Perbedaan antara rekomendasi AI dan keputusan manusia mudah saya pahami.",
    },
    {
        "id": "DQ4",
        "text": "Mekanisme Human Override mudah saya pahami.",
    },
    {
        "id": "DQ5",
        "text": "Alur dari Stage 1 ke Stage 2 mudah saya pahami.",
    },
]


# ==============================================================================
# SECTION D: OPEN-ENDED DASHBOARD FEEDBACK (3 ITEMS)
# ==============================================================================

OPEN_ENDED_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "OQ1",
        "text": "Bagian mana dari dashboard yang paling membantu Anda memahami hasil screening? Jelaskan alasannya.",
    },
    {
        "id": "OQ2",
        "text": "Bagian mana dari dashboard yang menurut Anda paling membingungkan atau sulit dipahami?",
    },
    {
        "id": "OQ3",
        "text": "Apa perbaikan utama yang menurut Anda dapat membuat dashboard ini lebih mudah dipahami atau digunakan?",
    },
]


# ==============================================================================
# PRACTICE CASE P0 ONBOARDING SPECIFICATION
# ==============================================================================

PRACTICE_CASE_P0: Dict[str, Any] = {
    "case_id": "P0",
    "case_title": "Kasus Latihan P0 — Orientasi Alur Kerja (Bukan Data Pasien Nyata)",
    "description": (
        "Kasus latihan ini dirancang untuk memperkenalkan alur screening: melihat hasil AI, "
        "memeriksa penjelasan feature contribution, mencoba keputusan peninjauan manusia (Setuju / Override), "
        "dan memberikan umpan balik terstruktur. Kasus ini dikecualikan dari data analisis riset."
    ),
    "features": {
        "age": 48,
        "sex": "female",
        "bmi": 27.5,
        "waist_cm": 88.0,
        "hypertension_history": "no",
        "smoking_history": "no",
        "sedentary_minutes_day": 360,
    },
    "governance": {
        "is_practice": True,
        "excluded_from_learning": True,
        "excluded_from_research": True,
    }
}
