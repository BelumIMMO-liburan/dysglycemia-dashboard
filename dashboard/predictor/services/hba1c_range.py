"""
Deterministic Stage-2 HbA1c Laboratory Range Categorization Service
Phase D2.8 Implementation

Authoritative Reference:
American Diabetes Association (ADA) Standards of Care in Diabetes — 2026 (Section 2)
Cross-checked with NIDDK Clinical Guidance.

EPISTEMIC BOUNDARIES:
- This service is NOT a machine-learning model and does NOT call GAM inference.
- This service does NOT perform automated clinical diagnosis.
- Categorizes entered numeric HbA1c percentage into standard laboratory range categories.
- Operates strictly on Python Decimal arithmetic to prevent floating-point representation drift.
"""

from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from typing import Union

# Frozen Reference Rule Version
RANGE_RULE_VERSION = "ADA_2026_A1C_RANGE_V1"

# Frozen Reference Thresholds
NORMAL_THRESHOLD = Decimal("5.7")      # < 5.7% is Normal-range
DIABETES_THRESHOLD = Decimal("6.5")    # >= 6.5% is Diabetes-range

# Mathematical & Practical Input Safety Bounds
MIN_SAFE_HBA1C = Decimal("2.0")
MAX_SAFE_HBA1C = Decimal("25.0")

# Standard Mandatory Caveat
STANDARD_DIAGNOSTIC_CAVEAT = (
    "This range presentation is not an automated diagnosis. "
    "In the absence of unequivocal hyperglycemia, clinical diagnosis generally "
    "requires appropriate confirmatory testing. This prototype does not evaluate "
    "whether confirmation has occurred."
)

ASSAY_LIMITATION_NOTE = (
    "HbA1c interpretation can depend on laboratory method and clinical context. "
    "This research prototype categorizes the entered numeric value only."
)


class HbA1cValidationError(ValueError):
    """Raised when an entered HbA1c value fails domain safety or precision validation."""
    pass


@dataclass(frozen=True)
class HbA1cRangeResult:
    """Immutable result structure for Stage-2 HbA1c range categorization."""
    hba1c: Decimal
    range_code: str
    range_label: str
    rule_version: str
    interpretation_copy: str
    diagnostic_caveat: str
    assay_limitation_note: str


def classify_hba1c_range(hba1c_value: Union[Decimal, str, int, float]) -> HbA1cRangeResult:
    """
    Classifies a validated HbA1c percentage into an authoritative laboratory range.

    Parameters:
        hba1c_value: Decimal or string representation of HbA1c (e.g., Decimal("6.10") or "6.10").
                     Floats are strictly rejected to ensure no floating-point precision loss.

    Returns:
        HbA1cRangeResult with range code, human-readable label, and required medical caveats.

    Raises:
        HbA1cValidationError: If value is not finite, negative, non-numeric, or outside safety bounds.
    """
    if isinstance(hba1c_value, float):
        raise HbA1cValidationError(
            "Float types are prohibited for clinical range determination. "
            "Supply a Decimal or string representation to maintain exact decimal precision."
        )

    try:
        if isinstance(hba1c_value, Decimal):
            d_val = hba1c_value
        else:
            d_val = Decimal(str(hba1c_value).strip())
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise HbA1cValidationError(f"Invalid numeric HbA1c value: '{hba1c_value}'") from exc

    if not d_val.is_finite():
        raise HbA1cValidationError("HbA1c value must be a finite number.")

    if d_val <= Decimal("0"):
        raise HbA1cValidationError("HbA1c percentage must be greater than 0.")

    if d_val < MIN_SAFE_HBA1C or d_val > MAX_SAFE_HBA1C:
        raise HbA1cValidationError(
            f"HbA1c value {d_val}% is outside practical input validation bounds "
            f"({MIN_SAFE_HBA1C}% to {MAX_SAFE_HBA1C}%)."
        )

    # Deterministic classification against frozen boundaries
    if d_val < NORMAL_THRESHOLD:
        code = "normal_range"
        label = "Normal-range"
        copy = "Entered HbA1c falls below the 5.7% prediabetes-range threshold."
    elif d_val < DIABETES_THRESHOLD:
        code = "prediabetes_range"
        label = "Prediabetes-range"
        copy = "Entered HbA1c falls within the 5.7% to <6.5% laboratory range."
    else:
        code = "diabetes_range"
        label = "Diabetes-range"
        copy = (
            "Entered HbA1c falls within the ≥6.5% laboratory range used in diabetes diagnostic criteria. "
            "This prototype does not establish a diagnosis; clinical diagnosis may require confirmatory "
            "testing and additional clinical context."
        )

    return HbA1cRangeResult(
        hba1c=d_val,
        range_code=code,
        range_label=label,
        rule_version=RANGE_RULE_VERSION,
        interpretation_copy=copy,
        diagnostic_caveat=STANDARD_DIAGNOSTIC_CAVEAT,
        assay_limitation_note=ASSAY_LIMITATION_NOTE,
    )
