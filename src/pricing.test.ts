import { describe, expect, it } from 'vitest';
import { estimate, formatRange, type EstimateInput } from './pricing';

const base: EstimateInput = {
  diameters: [],
  cleanup: false,
  restoration: false,
  nearStructure: 'no',
  rockBed: 'no',
  tightAccess: 'no',
};

function priceFor(input: Partial<EstimateInput>): string {
  const result = estimate({ ...base, ...input });
  if (result.kind !== 'price') {
    throw new Error(`expected a price, got ${JSON.stringify(result)}`);
  }
  return formatRange(result.low, result.high);
}

describe('required cases', () => {
  it('one 12" stump', () => {
    expect(priceFor({ diameters: ['12'] })).toBe('$125–$150');
  });

  it('one 30" stump', () => {
    expect(priceFor({ diameters: ['30'] })).toBe('$180–$215');
  });

  it('three stumps 24", 18", 12"', () => {
    expect(priceFor({ diameters: ['24', '18', '12'] })).toBe('$325–$390');
  });

  it('same three + cleanup', () => {
    expect(priceFor({ diameters: ['24', '18', '12'], cleanup: true })).toBe('$475–$570');
  });

  it('same three + restoration, cleanup auto-added', () => {
    expect(priceFor({ diameters: ['24', '18', '12'], restoration: true })).toBe('$675–$810');
  });

  it('one 20" + restoration', () => {
    expect(priceFor({ diameters: ['20'], restoration: true })).toBe('$475–$570');
  });

  it('one 30" + near house', () => {
    expect(priceFor({ diameters: ['30'], nearStructure: 'yes' })).toBe('$230–$275');
  });

  it('one 12" + rock bed', () => {
    expect(priceFor({ diameters: ['12'], rockBed: 'yes' })).toBe('$200–$240');
  });

  it('one 20" + "not sure" on all three difficulty questions', () => {
    const input: EstimateInput = {
      ...base,
      diameters: ['20'],
      nearStructure: 'not-sure',
      rockBed: 'not-sure',
      tightAccess: 'not-sure',
    };
    expect(priceFor(input)).toBe('$300–$360');
    const result = estimate(input);
    expect(result.kind === 'price' && result.confirmOnSite).toBe(true);
  });

  it('three stumps 24", 18", 12" + tight access + cleanup', () => {
    expect(
      priceFor({ diameters: ['24', '18', '12'], tightAccess: 'yes', cleanup: true }),
    ).toBe('$525–$630');
  });

  it('a 61" stump is call for a quote', () => {
    expect(estimate({ ...base, diameters: ['61'] })).toEqual({ kind: 'call' });
  });

  it.each(['0', '-5', '', '   ', 'abc', '12abc'])('diameter %j is an error with no price', (value) => {
    const result = estimate({ ...base, diameters: [value] });
    expect(result.kind).toBe('error');
    expect(result).not.toHaveProperty('low');
    expect(result).not.toHaveProperty('high');
  });
});

describe('edge cases', () => {
  it('a 60" stump is still priced', () => {
    expect(priceFor({ diameters: ['60'] })).toBe('$360–$430');
  });

  it('one stump over 60" among others makes the whole job call for a quote', () => {
    expect(estimate({ ...base, diameters: ['12', '61'] })).toEqual({ kind: 'call' });
  });

  it('an invalid row wins over a stump over 60"', () => {
    expect(estimate({ ...base, diameters: ['61', 'abc'] }).kind).toBe('error');
  });

  it('reports which row is invalid', () => {
    const result = estimate({ ...base, diameters: ['12', '0', '18'] });
    expect(result.kind).toBe('error');
    if (result.kind === 'error') {
      expect(result.errors.map((e) => e.row)).toEqual([1]);
    }
  });

  it('no stumps is an error', () => {
    expect(estimate(base).kind).toBe('error');
  });

  it('confirmOnSite is false when no question is "not sure"', () => {
    const result = estimate({ ...base, diameters: ['20'], rockBed: 'yes' });
    expect(result.kind === 'price' && result.confirmOnSite).toBe(false);
  });

  it('rounds ties up to the nearest $5', () => {
    // 21.25" × $6 = $127.50 → $130; × 1.2 = $153 → $155
    expect(priceFor({ diameters: ['21.25'] })).toBe('$130–$155');
  });

  it('formats thousands with a comma', () => {
    expect(priceFor({ diameters: ['60', '60', '60'] })).toBe('$1,080–$1,295');
  });
});
