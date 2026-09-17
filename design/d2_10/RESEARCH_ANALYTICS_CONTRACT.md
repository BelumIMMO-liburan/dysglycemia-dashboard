# Research Analytics Contract & Data Specification

**Phase:** D2.10 — Research Analytics + Human–AI Decision Flow  
**Module:** `dashboard/predictor/services/research_analytics.py`  
**Status:** Frozen & Verified

---

## 1. Architectural Role & Boundary
The `ResearchAnalyticsService` provides centralized, deterministic computation of all research-safe aggregate surveillance metrics across the two-stage dysglycemia screening prototype.

### Core Contract Invariants:
1. **Zero Database Writes:** Execution performs 0 database insertions, 0 updates, 0 deletes, and alters 0 timestamps.
2. **Zero ML/XAI Execution:** Performs 0 GAM predictions, 0 feature scalings, 0 additive contribution calculations, and 0 HbA1c reference range reclassifications.
3. **Pure Aggregate Consumption:** Computes metrics dynamically via bounded Django ORM aggregation queries from authoritative persisted models (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`).
4. **Zero Persistent Analytics Cache:** No intermediate aggregate tables, materialized views, or scheduled ETL processes.

---

## 2. Typed Data Contracts

### 2.1 DecisionTransitionMatrix
```python
@dataclass(frozen=True)
class DecisionTransitionMatrix:
    ai_refer_human_refer: int       # Concordant referral (Agreement)
    ai_refer_human_no_refer: int    # Override away from referral (Override)
    ai_no_refer_human_no_refer: int # Concordant non-referral (Agreement)
    ai_no_refer_human_refer: int    # Override toward referral (Override)

    @property
    def total_cells(self) -> int:
        return (
            self.ai_refer_human_refer
            + self.ai_refer_human_no_refer
            + self.ai_no_refer_human_no_refer
            + self.ai_no_refer_human_refer
        )

    @property
    def diagonal_sum(self) -> int:
        return self.ai_refer_human_refer + self.ai_no_refer_human_no_refer

    @property
    def off_diagonal_sum(self) -> int:
        return self.ai_refer_human_no_refer + self.ai_no_refer_human_refer
```

### 2.2 OverrideReasonSummary
```python
@dataclass(frozen=True)
class OverrideReasonSummary:
    code: str
    label: str
    count: int
    rate: Optional[float]  # None if branch denominator is zero
```

### 2.3 ResearchAnalyticsSnapshot
```python
@dataclass(frozen=True)
class ResearchAnalyticsSnapshot:
    total_screenings: int
    ai_refer_count: int
    ai_no_refer_count: int
    ai_refer_rate: Optional[float]

    review_eligible_count: int
    explanation_unavailable_count: int
    explanation_generated_count: int
    explanation_availability_rate: Optional[float]
    reviewed_count: int
    review_completion_rate: Optional[float]

    accepted_count: int
    overridden_count: int
    agreement_rate: Optional[float]
    override_rate: Optional[float]

    final_refer_count: int
    final_no_refer_count: int
    final_referral_rate: Optional[float]

    stage2_eligible_count: int
    stage2_completed_count: int
    stage2_completion_rate: Optional[float]

    transition_matrix: DecisionTransitionMatrix

    override_away_count: int
    override_toward_count: int
    override_away_rate: Optional[float]
    override_toward_rate: Optional[float]

    reasons_refer_to_no_refer: List[OverrideReasonSummary]
    reasons_no_refer_to_refer: List[OverrideReasonSummary]
    all_override_reasons: List[OverrideReasonSummary]

    stage2_normal_count: int
    stage2_prediabetes_count: int
    stage2_diabetes_count: int
    stage2_normal_rate: Optional[float]
    stage2_prediabetes_rate: Optional[float]
    stage2_diabetes_rate: Optional[float]

    date_from: Optional[date]
    date_to: Optional[date]

    data_integrity_passed: bool
    data_integrity_warnings: List[str]
```

---

## 3. Query Boundary & Computational Guarantee
The entire snapshot is computed using **exactly 2 bounded SQL queries**:
1. **Query 1:** Single aggregate query over `ScreeningRecord` using `Count(filter=Q(...))` joins across `explanation`, `human_review`, and `stage2_assessment`.
2. **Query 2:** Single grouped aggregate query over `HumanReview` where `review_action == 'overridden'`, grouping by `override_reason_code` and AI recommendation boolean.

This guarantees a bounded, constant number of SQL queries per rendered page, eliminating $N+1$ query loops regardless of intake database volume.
