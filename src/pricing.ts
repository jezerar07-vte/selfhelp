export type Answer = 'yes' | 'no' | 'not-sure';

export interface EstimateInput {
  diameters: string[];
  cleanup: boolean;
  restoration: boolean;
  nearStructure: Answer;
  rockBed: Answer;
  tightAccess: Answer;
}

export type EstimateResult =
  | { kind: 'price'; low: number; high: number; confirmOnSite: boolean }
  | { kind: 'call' }
  | { kind: 'error'; errors: { row: number; message: string }[] };

export const PRICE_PER_INCH = 6;
export const MINIMUM_GRINDING = 125;
export const CLEANUP_PRICE = 150;
export const RESTORATION_PRICE = 200;
export const NEAR_STRUCTURE_PRICE = 50;
export const ROCK_BED_PRICE = 75;
export const TIGHT_ACCESS_PRICE = 50;
export const MAX_DIAMETER_INCHES = 60;
export const HIGH_MULTIPLIER_PERCENT = 120;
export const ROUND_TO = 5;

const DECIMAL_PATTERN = /^(-?)(?=\.?\d)(\d*)(?:\.(\d+))?$/;

function roundCentsToStep(cents: number): number {
  const step = ROUND_TO * 100;
  return Math.floor((cents + step / 2) / step) * step;
}

function surcharge(answer: Answer, price: number): number {
  return answer === 'no' ? 0 : price;
}

export function estimate(input: EstimateInput): EstimateResult {
  if (input.diameters.length === 0) {
    return {
      kind: 'error',
      errors: [{ row: 0, message: 'Enter the diameter of at least one stump.' }],
    };
  }

  const hundredths: number[] = [];
  const errors: { row: number; message: string }[] = [];
  input.diameters.forEach((raw, row) => {
    const text = raw.trim();
    const match = DECIMAL_PATTERN.exec(text);
    if (text === '') {
      errors.push({ row, message: 'Enter a diameter in inches.' });
    } else if (!match) {
      errors.push({ row, message: 'Diameter must be a number, like 12 or 18.5.' });
    } else {
      const [, sign, whole, fraction = ''] = match;
      if (fraction.length > 2) {
        errors.push({ row, message: 'Use at most 2 decimal places.' });
        return;
      }
      // Integer hundredths of an inch; a huge digit string becomes Infinity (> max, so "call").
      const value = Number(whole || '0') * 100 + Number(fraction.padEnd(2, '0'));
      if (sign === '-' || value === 0) {
        errors.push({ row, message: 'Diameter must be greater than zero.' });
      } else {
        hundredths.push(value);
      }
    }
  });
  if (errors.length > 0) return { kind: 'error', errors };

  if (hundredths.some((v) => v > MAX_DIAMETER_INCHES * 100)) return { kind: 'call' };

  // hundredths of an inch × $6/inch = whole cents, so this is exact.
  const grindingCents = Math.max(
    hundredths.reduce((sum, v) => sum + v, 0) * PRICE_PER_INCH,
    MINIMUM_GRINDING * 100,
  );

  let extras = 0;
  if (input.cleanup || input.restoration) extras += CLEANUP_PRICE;
  if (input.restoration) extras += RESTORATION_PRICE;
  extras += surcharge(input.nearStructure, NEAR_STRUCTURE_PRICE);
  extras += surcharge(input.rockBed, ROCK_BED_PRICE);
  extras += surcharge(input.tightAccess, TIGHT_ACCESS_PRICE);

  const totalCents = grindingCents + extras * 100;
  const step = ROUND_TO * 100;
  // Round the unrounded high end once: floor((total * pct / 100 + step / 2) / step) * step.
  const highRoundedCents =
    Math.floor((totalCents * HIGH_MULTIPLIER_PERCENT + 50 * step) / (100 * step)) * step;

  return {
    kind: 'price',
    low: roundCentsToStep(totalCents) / 100,
    high: highRoundedCents / 100,
    confirmOnSite: [input.nearStructure, input.rockBed, input.tightAccess].includes('not-sure'),
  };
}

export function formatRange(low: number, high: number): string {
  const fmt = (n: number) => `$${n.toLocaleString('en-US')}`;
  return `${fmt(low)}–${fmt(high)}`;
}
