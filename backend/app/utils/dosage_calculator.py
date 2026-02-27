"""
Dosage calculation utilities.
Provides functions for calculating daily doses, unit conversions,
and dosage schedule generation.
"""

from datetime import datetime, time, timedelta, timezone
from typing import List, Optional, Tuple

# Conversion factors to mg
UNIT_CONVERSIONS = {
    "g": 1000.0,
    "mg": 1.0,
    "mcg": 0.001,
    "ug": 0.001,
    "ml": None,  # Depends on concentration
    "UI": None,  # International units - drug specific
    "mmol": None,  # Depends on molecule
}


def parse_frequency(frequency: str) -> int:
    """
    Parse a frequency string and return the number of doses per day.

    Supported formats:
    - "1x/day", "2x/day", "3x/day" etc.
    - "q8h", "q12h", "q6h" etc.
    - "bid" (2x/day), "tid" (3x/day), "qid" (4x/day)
    - "daily" (1x/day)
    """
    freq_lower = frequency.lower().strip()

    # Format: Nx/day or Nx/jour
    if "/day" in freq_lower or "/jour" in freq_lower:
        try:
            return int(freq_lower.split("x")[0])
        except (ValueError, IndexError):
            return 1

    # Format: qNh (every N hours)
    if freq_lower.startswith("q") and "h" in freq_lower:
        try:
            hours = int(freq_lower.replace("q", "").replace("h", ""))
            return max(1, 24 // hours)
        except (ValueError, ZeroDivisionError):
            return 1

    # Latin abbreviations
    LATIN_FREQ = {
        "daily": 1,
        "od": 1,
        "bid": 2,
        "tid": 3,
        "qid": 4,
        "qd": 1,
        "hs": 1,  # at bedtime
        "prn": 0,  # as needed
    }

    return LATIN_FREQ.get(freq_lower, 1)


def calculate_daily_dose(
    dosage_value: float,
    dosage_unit: str,
    frequency: str,
) -> Tuple[float, str]:
    """
    Calculate the total daily dose.
    Returns (daily_dose, unit).
    """
    doses_per_day = parse_frequency(frequency)
    daily_dose = dosage_value * doses_per_day
    return daily_dose, dosage_unit


def convert_to_mg(value: float, unit: str) -> Optional[float]:
    """Convert a dose value to milligrams. Returns None if conversion not possible."""
    factor = UNIT_CONVERSIONS.get(unit.lower())
    if factor is not None:
        return value * factor
    return None


def generate_schedule_times(
    frequency: str,
    start_hour: int = 8,
) -> List[time]:
    """
    Generate a list of administration times based on frequency.

    Args:
        frequency: Frequency string (e.g., "3x/day")
        start_hour: Hour to start the first dose (default 8 AM)

    Returns:
        List of time objects for each dose
    """
    doses_per_day = parse_frequency(frequency)

    if doses_per_day <= 0:
        return []

    if doses_per_day == 1:
        return [time(start_hour, 0)]

    interval_hours = 24 // doses_per_day
    times = []
    current_hour = start_hour

    for _ in range(doses_per_day):
        times.append(time(current_hour % 24, 0))
        current_hour += interval_hours

    return sorted(times)


def generate_administration_schedule(
    start_date: datetime,
    end_date: Optional[datetime],
    frequency: str,
    start_hour: int = 8,
) -> List[datetime]:
    """
    Generate a full administration schedule between two dates.

    Returns a list of datetime objects for each scheduled administration.
    """
    if not end_date:
        # Default to 7 days if no end date
        end_date = start_date + timedelta(days=7)

    schedule_times = generate_schedule_times(frequency, start_hour)
    schedule = []

    current_date = start_date.date()
    end = end_date.date()

    while current_date <= end:
        for t in schedule_times:
            scheduled_dt = datetime.combine(
                current_date, t, tzinfo=timezone.utc
            )
            if start_date <= scheduled_dt <= end_date:
                schedule.append(scheduled_dt)
        current_date += timedelta(days=1)

    return schedule
