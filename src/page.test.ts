import { describe, expect, it } from 'vitest';
import html from '../index.html?raw';
import css from './style.css?raw';

const doc = new DOMParser().parseFromString(html, 'text/html');
const TEL = 'tel:+16264944809';

describe('page', () => {
  it('has sections in order and an empty estimator root', () => {
    const ids = ['home', 'services', 'estimator', 'contact'];
    const els = ids.map((id) => doc.getElementById(id));
    els.forEach((el) => expect(el).not.toBeNull());
    for (let i = 0; i < els.length - 1; i++) {
      const pos = els[i]!.compareDocumentPosition(els[i + 1]!);
      expect(pos & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
    const root = doc.getElementById('estimator-root');
    expect(root).not.toBeNull();
    expect(root!.innerHTML).toBe('');
  });

  it('wraps every phone number mention in a tel link', () => {
    const smsLinks = Array.from(doc.querySelectorAll('a[href^="sms:"]'));
    const mentions = Array.from(doc.body.querySelectorAll('*')).filter(
      (el) =>
        el.tagName !== 'SCRIPT' &&
        Array.from(el.childNodes).some(
          (n) => n.nodeType === Node.TEXT_NODE && n.textContent!.includes('494-4809'),
        ),
    );
    expect(mentions.length).toBeGreaterThan(0);
    for (const el of mentions) {
      if (smsLinks.some((s) => s.contains(el))) continue;
      const a = el.closest('a');
      expect(a?.getAttribute('href')).toBe(TEL);
    }
  });

  it('has mailto and sms links', () => {
    expect(doc.querySelector('a[href="mailto:jezerar07@gmail.com"]')).not.toBeNull();
    expect(doc.querySelector('a[href="sms:+16264944809"]')).not.toBeNull();
  });

  it('has the 811 line in services', () => {
    expect(doc.getElementById('services')!.textContent).toContain(
      'We call 811 (Gopher State One Call) before every job',
    );
  });

  it('shows the service area in contact', () => {
    expect(doc.getElementById('contact')!.textContent).toContain(
      'Shakopee, MN, surrounding areas, and the Twin Cities metro',
    );
  });

  it('contains no invented claims in visible text', () => {
    const text = doc.body.textContent!.toLowerCase();
    for (const word of [
      'review',
      'testimonial',
      'licensed',
      'insured',
      'years of experience',
      'award',
      'guarantee',
      'free estimate',
      'same-day',
      'rated',
    ]) {
      expect(text).not.toContain(word);
    }
  });

  it('lists the given restoration and winter details in services', () => {
    const text = doc.getElementById('services')!.textContent!;
    for (const s of [
      'Black dirt backfill',
      'grass seed',
      'Snow removal',
      'winter cleanups',
      'Seasonal',
      'Call for a quote',
    ]) {
      expect(text).toContain(s);
    }
    expect(text).not.toContain('below the surface');
  });

  it('has at least one placeholder', () => {
    expect(doc.querySelectorAll('.placeholder').length).toBeGreaterThan(0);
  });

  it('keeps nav link labels on one line', () => {
    const rule = css.match(/\.nav-list\s+a\s*\{[^}]*\}/);
    expect(rule).not.toBeNull();
    expect(rule![0]).toMatch(/white-space\s*:\s*nowrap/);
  });
});
