// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest';
import { mountEstimator } from './estimator';
import css from './style.css?raw';

let root: HTMLElement;

function inputs(): HTMLInputElement[] {
  return Array.from(root.querySelectorAll<HTMLInputElement>('input[type="text"]'));
}
function type(i: number, value: string): void {
  const input = inputs()[i];
  input.value = value;
  input.dispatchEvent(new Event('input', { bubbles: true }));
}
function button(name: string): HTMLButtonElement {
  const b = Array.from(root.querySelectorAll('button')).find((x) => x.textContent === name);
  if (!b) throw new Error(`no button ${name}`);
  return b;
}
function check(box: HTMLInputElement, checked: boolean): void {
  box.checked = checked;
  box.dispatchEvent(new Event('change', { bubbles: true }));
}
function checkbox(startsWith: string): HTMLInputElement {
  const label = Array.from(root.querySelectorAll('label')).find((l) =>
    l.textContent?.startsWith(startsWith),
  );
  const box = label?.querySelector<HTMLInputElement>('input[type="checkbox"]');
  if (!box) throw new Error(`no checkbox ${startsWith}`);
  return box;
}
function choose(question: string, answer: string): void {
  const fs = Array.from(root.querySelectorAll('fieldset')).find(
    (f) => f.querySelector('legend')?.textContent?.startsWith(question),
  );
  const radio = Array.from(fs?.querySelectorAll<HTMLInputElement>('input[type="radio"]') ?? []).find(
    (r) => r.parentElement?.textContent === answer,
  );
  if (!radio) throw new Error(`no radio ${question}/${answer}`);
  radio.checked = true;
  radio.dispatchEvent(new Event('change', { bubbles: true }));
}
const result = () => root.querySelector('[aria-live="polite"]') as HTMLElement;
const CLEANUP = 'Cleanup and haul away';
const RESTORATION = 'Restoration';

beforeEach(() => {
  document.body.textContent = '';
  root = document.createElement('div');
  document.body.append(root);
  mountEstimator(root);
});

describe('estimator', () => {
  it('starts with one row and a neutral prompt', () => {
    expect(inputs()).toHaveLength(1);
    expect(result().textContent).toContain('Enter a diameter for each stump to see your estimate.');
    expect(result().textContent).not.toContain('$');
    expect(root.querySelector('[aria-invalid]')).toBeNull();
  });

  it('prices a single stump', () => {
    type(0, '12');
    expect(result().textContent).toContain('$125–$150');
  });

  it('prices three stumps with cleanup', () => {
    button('Add another stump').click();
    button('Add another stump').click();
    type(0, '24');
    type(1, '18');
    type(2, '12');
    check(checkbox(CLEANUP), true);
    expect(result().textContent).toContain('$475–$570');
  });

  it('restoration checks and disables cleanup', () => {
    button('Add another stump').click();
    button('Add another stump').click();
    type(0, '24');
    type(1, '18');
    type(2, '12');
    const cleanup = checkbox(CLEANUP);
    check(checkbox(RESTORATION), true);
    expect(cleanup.checked).toBe(true);
    expect(cleanup.disabled).toBe(true);
    expect(root.textContent).toContain('Included with restoration');
    expect(result().textContent).toContain('$675–$810');
    check(checkbox(RESTORATION), false);
    expect(cleanup.disabled).toBe(false);
    expect(cleanup.checked).toBe(true);
  });

  it('adds the near-structure surcharge', () => {
    type(0, '30');
    choose('Is any stump within 3 feet', 'Yes');
    expect(result().textContent).toContain('$230–$275');
  });

  it('handles Not sure on all questions', () => {
    type(0, '20');
    choose('Is any stump within 3 feet', 'Not sure');
    choose('Is any stump in a rock bed', 'Not sure');
    choose('Is the only access', 'Not sure');
    expect(result().textContent).toContain('$300–$360');
    const msgs = Array.from(root.querySelectorAll('p')).filter(
      (p) => p.textContent === "We'll confirm on-site." && !p.hidden,
    );
    expect(msgs).toHaveLength(3);
  });

  it('asks for a call over 60 inches', () => {
    type(0, '61');
    expect(result().textContent).toContain('Call for a quote');
    expect(result().textContent).not.toContain('$');
    expect(result().querySelector('a[href="tel:+16264944809"]')?.textContent).toBe('(626) 494-4809');
  });

  it.each(['abc', '0', '-5'])('shows an error for %s', (value) => {
    type(0, value);
    const input = inputs()[0];
    expect(input.getAttribute('aria-invalid')).toBe('true');
    const err = document.getElementById(input.getAttribute('aria-describedby') ?? '');
    expect(err?.textContent).toBeTruthy();
    expect(result().textContent).not.toContain('$');
  });

  it('shows an error after clearing a typed value', () => {
    type(0, '12');
    type(0, '');
    const input = inputs()[0];
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(document.getElementById(input.getAttribute('aria-describedby') ?? '')?.textContent).toBe(
      'Enter a diameter in inches.',
    );
    expect(result().textContent).not.toContain('$');
  });

  it('lists every error in the result area with its stump number', () => {
    button('Add another stump').click();
    type(0, 'abc');
    type(1, '0');
    const text = result().textContent ?? '';
    expect(text).toContain('Check stump 1: ');
    expect(text).toContain('Check stump 2: ');
    expect(text).not.toContain('$');
  });

  it('keeps an untouched blank row free of errors', () => {
    button('Add another stump').click();
    type(0, 'abc');
    expect(inputs()[0].getAttribute('aria-invalid')).toBe('true');
    expect(inputs()[1].hasAttribute('aria-invalid')).toBe(false);
    expect(result().textContent).toContain('Enter a diameter for each stump');
  });

  it('adds, removes, and renumbers rows', () => {
    expect(button('Remove').disabled).toBe(true);
    button('Add another stump').click();
    expect(inputs()).toHaveLength(2);
    expect(document.activeElement).toBe(inputs()[1]);
    expect(button('Remove').disabled).toBe(false);
    button('Add another stump').click();
    Array.from(root.querySelectorAll('button')).find((b) => b.textContent === 'Remove')?.click();
    const labels = Array.from(root.querySelectorAll('.est-row label')).map((l) => l.textContent);
    expect(labels).toEqual(['Stump 1 diameter (inches)', 'Stump 2 diameter (inches)']);
    Array.from(root.querySelectorAll('button')).find((b) => b.textContent === 'Remove')?.click();
    expect(inputs()).toHaveLength(1);
    expect(button('Remove').disabled).toBe(true);
  });

  it('always shows the on-site note and the text link', () => {
    const note =
      'Final price confirmed on-site. Surface roots, hardwoods, tight access, and travel outside the Shakopee area may change the price.';
    for (const v of ['', '12', '61', 'abc']) {
      type(0, v);
      expect(root.textContent).toContain(note);
      expect(root.querySelector('a[href="sms:+16264944809"]')).not.toBeNull();
    }
  });

  it('stylesheet keeps the hidden attribute authoritative', () => {
    expect(css).toMatch(/\[hidden\]\s*\{[^}]*display:\s*none\s*!important/);
  });

  it('stylesheet never wraps phone links', () => {
    expect(css).toMatch(/a\[href\^=['"]tel:['"]\]\s*\{[^}]*white-space:\s*nowrap/);
  });

  it('stylesheet gives the result tel link a 44px tap target', () => {
    expect(css).toMatch(
      /\.est-result\s+a\[href\^=['"]tel:['"]\][^{]*\{[^}]*min-height:\s*44px/,
    );
  });
});
