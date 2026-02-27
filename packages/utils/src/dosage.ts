/**
 * Parse a frequency string and return doses per day.
 */
export function parseFrequency(frequency: string): number {
  const freq = frequency.toLowerCase().trim();

  // Format: Nx/day or Nx/jour
  if (freq.includes('/day') || freq.includes('/jour')) {
    const match = freq.match(/^(\d+)/);
    return match ? parseInt(match[1], 10) : 1;
  }

  // Format: qNh (every N hours)
  if (freq.startsWith('q') && freq.includes('h')) {
    const hours = parseInt(freq.replace('q', '').replace('h', ''), 10);
    return hours > 0 ? Math.floor(24 / hours) : 1;
  }

  // Latin abbreviations
  const latinFreq: Record<string, number> = {
    daily: 1,
    od: 1,
    bid: 2,
    tid: 3,
    qid: 4,
    qd: 1,
    hs: 1,
    prn: 0,
  };

  return latinFreq[freq] ?? 1;
}

/**
 * Calculate total daily dose.
 */
export function calculateDailyDose(
  dosageValue: number,
  frequency: string,
): number {
  return dosageValue * parseFrequency(frequency);
}

/**
 * Generate schedule times for a given frequency.
 */
export function generateScheduleTimes(
  frequency: string,
  startHour: number = 8,
): string[] {
  const dosesPerDay = parseFrequency(frequency);
  if (dosesPerDay <= 0) return [];

  const intervalHours = Math.floor(24 / dosesPerDay);
  const times: string[] = [];
  let currentHour = startHour;

  for (let i = 0; i < dosesPerDay; i++) {
    const hour = currentHour % 24;
    times.push(`${hour.toString().padStart(2, '0')}:00`);
    currentHour += intervalHours;
  }

  return times.sort();
}

/**
 * Format a dosage for display.
 */
export function formatDosage(
  value: number,
  unit: string,
  frequency: string,
): string {
  return `${value} ${unit} ${frequency}`;
}
