import { beforeEach, describe, expect, it } from 'vitest';
import homeHtml from '../index.html?raw';
import servicesHtml from '../services.html?raw';
import estimatorHtml from '../estimator.html?raw';
import contactHtml from '../contact.html?raw';
import css from './style.css?raw';
import { setupNav } from './nav';

const parse = (html: string) => new DOMParser().parseFromString(html, 'text/html');

const PAGES = {
  'index.html': parse(homeHtml),
  'services.html': parse(servicesHtml),
  'estimator.html': parse(estimatorHtml),
  'contact.html': parse(contactHtml),
};
const ENTRIES = Object.entries(PAGES);
const home = PAGES['index.html'];
const services = PAGES['services.html'];
const estimator = PAGES['estimator.html'];
const contact = PAGES['contact.html'];

const TEL = 'tel:+16264944809';
const SERVICE_AREA = 'Shakopee, MN, surrounding areas, and the Twin Cities metro';

// Header markup with the per-page active marker removed, so all pages can be compared.
function normalizedHeader(doc: Document): string {
  const header = doc.querySelector('header')!.cloneNode(true) as Element;
  header.querySelectorAll('[aria-current]').forEach((el) => el.removeAttribute('aria-current'));
  return header.outerHTML.replace(/\s+/g, ' ');
}

describe.each(ENTRIES)('%s', (file, doc) => {
  it('has a title with the business name, a description, and a viewport meta', () => {
    expect(doc.title).toContain('High Gear Stump Services');
    expect(doc.querySelector('meta[name="description"]')?.getAttribute('content')).toBeTruthy();
    expect(doc.querySelector('meta[name="viewport"]')).not.toBeNull();
  });

  it('loads Oswald and Inter from Google Fonts', () => {
    const href = doc.querySelector('link[href^="https://fonts.googleapis.com/"]')?.getAttribute('href');
    expect(href).toContain('Oswald');
    expect(href).toContain('Inter');
  });

  it('has nav links to all four pages and marks only this page as current', () => {
    const nav = doc.querySelector('header nav')!;
    expect(nav).not.toBeNull();
    for (const target of Object.keys(PAGES)) {
      expect(nav.querySelector(`a[href="${target}"]`)).not.toBeNull();
    }
    const current = doc.querySelectorAll('header [aria-current="page"]');
    expect(current.length).toBe(1);
    expect(current[0].getAttribute('href')).toBe(file);
  });

  it('has a "Get a Quote" link to the estimator in the header', () => {
    const cta = Array.from(doc.querySelectorAll('header a')).find(
      (a) => a.textContent!.trim() === 'Get a Quote',
    );
    expect(cta?.getAttribute('href')).toBe('estimator.html');
  });

  it('has a hamburger button wired to the nav list', () => {
    const button = doc.querySelector('header button[aria-controls]')!;
    expect(button).not.toBeNull();
    expect(button.getAttribute('aria-expanded')).toBe('false');
    expect(button.getAttribute('aria-label') ?? button.textContent).toBeTruthy();
    const list = doc.getElementById(button.getAttribute('aria-controls')!);
    expect(list).not.toBeNull();
    expect(list!.closest('nav')).not.toBeNull();
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
    for (const el of mentions) {
      if (smsLinks.some((s) => s.contains(el))) continue;
      expect(el.closest('a')?.getAttribute('href')).toBe(TEL);
    }
  });

  it('contains no invented claims in visible text', () => {
    const text = doc.body.textContent!.toLowerCase();
    for (const phrase of [
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
      expect(text).not.toContain(phrase);
    }
    for (const word of [
      'best',
      'professional',
      'affordable',
      'fast',
      'reliable',
      'trusted',
      'quality',
      'expert',
      'experienced',
      'satisfaction',
    ]) {
      expect(text).not.toMatch(new RegExp(`\\b${word}\\b`));
    }
  });

  it('uses no photos', () => {
    expect(doc.querySelectorAll('img, picture').length).toBe(0);
  });
});

describe('shared layout', () => {
  it('uses the same header on every page', () => {
    const headers = ENTRIES.map(([, doc]) => normalizedHeader(doc));
    headers.forEach((h) => expect(h).toBe(headers[0]));
  });

  it('uses the same footer on every page', () => {
    const footers = ENTRIES.map(([, doc]) => doc.querySelector('footer')!.outerHTML.replace(/\s+/g, ' '));
    footers.forEach((f) => expect(f).toBe(footers[0]));
  });

  it('puts a caution stripe divider on at least two pages', () => {
    const withStripe = ENTRIES.filter(([, doc]) => doc.querySelector('.caution-stripe'));
    expect(withStripe.length).toBeGreaterThanOrEqual(2);
  });
});

describe('home page', () => {
  it('has the hero headline and service area line', () => {
    expect(home.querySelector('h1')!.textContent!.trim()).toBe(
      'Stump Grinding in Shakopee & the Twin Cities',
    );
    const hero = home.querySelector('h1')!.closest('section')!;
    expect(hero.textContent).toContain('Shakopee');
    expect(hero.textContent).toContain('Twin Cities metro');
  });

  it('has "Get an Estimate" and "Call Now" buttons in the hero', () => {
    const hero = home.querySelector('h1')!.closest('section')!;
    const links = Array.from(hero.querySelectorAll('a'));
    const estimate = links.find((a) => a.textContent!.trim() === 'Get an Estimate');
    const call = links.find((a) => a.textContent!.trim() === 'Call Now');
    expect(estimate?.getAttribute('href')).toBe('estimator.html');
    expect(call?.getAttribute('href')).toBe(TEL);
    expect(call?.getAttribute('aria-label')).toContain('(626) 494-4809');
  });

  it('has a gallery of before/after placeholders and nothing else in it', () => {
    const gallery = home.getElementById('gallery')!;
    expect(gallery).not.toBeNull();
    const boxes = gallery.querySelectorAll('.placeholder');
    expect(boxes.length).toBeGreaterThanOrEqual(2);
    boxes.forEach((box) => expect(box.textContent!.trim()).toBe('Before/after photo coming soon'));
  });
});

describe('services page', () => {
  const cards = Array.from(services.querySelectorAll('.service-card'));

  it('has one card per service, each with an inline SVG icon', () => {
    const titles = cards.map((c) => c.querySelector('h2, h3')!.textContent!.trim().toLowerCase());
    expect(titles).toEqual([
      'stump grinding',
      'root grinding',
      'cleanup and haul away',
      'yard restoration',
      'winter services',
    ]);
    cards.forEach((card) => expect(card.querySelector('svg')).not.toBeNull());
  });

  it('has the 811 line', () => {
    expect(services.body.textContent).toContain('We call 811 (Gopher State One Call) before every job');
  });

  it('lists the given restoration and winter details', () => {
    const text = services.body.textContent!;
    for (const s of ['Black dirt backfill', 'grass seed', 'Snow removal', 'winter cleanups', 'Seasonal', 'Call for a quote']) {
      expect(text).toContain(s);
    }
    expect(text).not.toContain('below the surface');
  });
});

describe('estimator page', () => {
  it('has an empty estimator root', () => {
    const root = estimator.getElementById('estimator-root');
    expect(root).not.toBeNull();
    expect(root!.innerHTML).toBe('');
  });
});

describe('contact page', () => {
  it('has tel, mailto and sms links', () => {
    expect(contact.querySelector(`main a[href="${TEL}"]`)).not.toBeNull();
    expect(contact.querySelector('a[href="mailto:jezerar07@gmail.com"]')).not.toBeNull();
    expect(contact.querySelector('a[href="sms:+16264944809"]')).not.toBeNull();
  });

  it('shows the service area and an hours placeholder', () => {
    expect(contact.body.textContent).toContain(SERVICE_AREA);
    const hours = Array.from(contact.querySelectorAll('.placeholder')).some((p) =>
      p.textContent!.toLowerCase().includes('hours'),
    );
    expect(hours).toBe(true);
  });
});

describe('stylesheet', () => {
  it('uses the brand colors', () => {
    for (const color of ['#111111', '#1e1e1e', '#ffc400']) {
      expect(css.toLowerCase()).toContain(color);
    }
  });

  it('sets Oswald and Inter with fallbacks', () => {
    expect(css).toMatch(/font-family\s*:\s*['"]?Oswald['"]?\s*,/);
    expect(css).toMatch(/font-family\s*:\s*['"]?Inter['"]?\s*,/);
  });

  it('draws the caution stripe with a repeating gradient', () => {
    const rule = css.match(/\.caution-stripe\s*\{[^}]*\}/);
    expect(rule).not.toBeNull();
    expect(rule![0]).toMatch(/repeating-linear-gradient/);
  });

  it('loads no external images', () => {
    expect(css).not.toMatch(/url\(\s*['"]?(https?:)?\/\//);
  });

  it('keeps nav link labels on one line', () => {
    const rule = css.match(/\.nav-list\s+a\s*\{[^}]*\}/);
    expect(rule).not.toBeNull();
    expect(rule![0]).toMatch(/white-space\s*:\s*nowrap/);
  });
});

describe('hamburger menu', () => {
  beforeEach(() => {
    document.body.innerHTML = home.querySelector('header')!.outerHTML;
    setupNav(document);
  });

  const button = () => document.querySelector<HTMLButtonElement>('header button[aria-controls]')!;

  it('opens and closes on click', () => {
    button().click();
    expect(button().getAttribute('aria-expanded')).toBe('true');
    button().click();
    expect(button().getAttribute('aria-expanded')).toBe('false');
  });

  it('closes on Escape and returns focus to the button', () => {
    button().click();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(button().getAttribute('aria-expanded')).toBe('false');
    expect(document.activeElement).toBe(button());
  });
});
