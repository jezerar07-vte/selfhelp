import {
  CLEANUP_PRICE,
  RESTORATION_PRICE,
  estimate,
  formatRange,
  type Answer,
  type EstimateResult,
} from './pricing';

const PHONE_TEL = 'tel:+16264944809';
const PHONE_SMS = 'sms:+16264944809';
const PHONE_DISPLAY = '(626) 494-4809';

const QUESTIONS = [
  { key: 'nearStructure', text: 'Is any stump within 3 feet of the house, foundation, fence, driveway, or patio?' },
  { key: 'rockBed', text: 'Is any stump in a rock bed, gravel, or landscaping edging?' },
  {
    key: 'tightAccess',
    text: 'Is the only access through a gate narrower than 36 inches, or up/down stairs or a steep slope?',
  },
] as const;

type QuestionKey = (typeof QUESTIONS)[number]['key'];

const ANSWERS: { value: Answer; label: string }[] = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
  { value: 'not-sure', label: 'Not sure' },
];

interface Row {
  id: number;
  value: string;
  touched: boolean;
  wrapper: HTMLElement;
  label: HTMLLabelElement;
  input: HTMLInputElement;
  error: HTMLElement;
  remove: HTMLButtonElement;
}

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function phoneLink(href: string, text: string): HTMLAnchorElement {
  const a = el('a', undefined, text);
  a.href = href;
  return a;
}

let mountCount = 0;

export function mountEstimator(root: HTMLElement): void {
  const uid = `est${mountCount++}`;
  let nextRowId = 0;
  const rows: Row[] = [];
  const answers: Record<QuestionKey, Answer> = { nearStructure: 'no', rockBed: 'no', tightAccess: 'no' };

  root.textContent = '';
  const form = el('div', 'estimator');
  root.append(form);

  // 1. Stump rows
  form.append(
    el(
      'p',
      'est-intro',
      'Add one row per stump. Measure the diameter in inches at ground level, across the widest point.',
    ),
  );
  const rowsBox = el('div', 'est-rows');
  const addButton = el('button', 'est-btn', 'Add another stump');
  addButton.type = 'button';
  form.append(rowsBox, addButton);

  // 2. Add-ons
  const addons = el('fieldset', 'est-group');
  addons.append(el('legend', undefined, 'Add-ons'));
  const makeCheck = (text: string) => {
    const label = el('label', 'est-check');
    const box = el('input');
    box.type = 'checkbox';
    const span = el('span', undefined, text);
    label.append(box, span);
    return { label, box, span };
  };
  const cleanup = makeCheck(`Cleanup and haul away (+$${CLEANUP_PRICE})`);
  const restoration = makeCheck(
    `Restoration: black dirt backfill + grass seed (+$${RESTORATION_PRICE})`,
  );
  const cleanupNote = el('span', 'est-note', 'Included with restoration');
  cleanupNote.hidden = true;
  cleanup.span.append(cleanupNote);
  addons.append(cleanup.label, restoration.label);
  form.append(addons);

  // 3. Difficulty
  const confirmBoxes = {} as Record<QuestionKey, HTMLElement>;
  for (const q of QUESTIONS) {
    const fs = el('fieldset', 'est-group');
    fs.append(el('legend', undefined, q.text));
    const options = el('div', 'est-options');
    fs.append(options);
    for (const a of ANSWERS) {
      const label = el('label', 'est-radio');
      const radio = el('input');
      radio.type = 'radio';
      radio.name = `${uid}-${q.key}`;
      radio.value = a.value;
      radio.checked = a.value === 'no';
      radio.addEventListener('change', () => {
        if (radio.checked) {
          answers[q.key] = a.value;
          update();
        }
      });
      label.append(radio, el('span', undefined, a.label));
      options.append(label);
    }
    const confirm = el('p', 'est-note');
    confirmBoxes[q.key] = confirm;
    fs.append(confirm);
    form.append(fs);
  }

  // 4. Result
  const result = el('div', 'est-result');
  result.setAttribute('aria-live', 'polite');
  const resultBody = el('div');
  result.append(
    resultBody,
    el(
      'p',
      'est-onsite',
      'Final price confirmed on-site. Surface roots, hardwoods, tight access, and travel outside the Shakopee area may change the price.',
    ),
  );
  form.append(result);

  // 5. Text link
  const text = el('a', 'btn btn-primary est-text', 'Text a photo for an exact quote');
  text.href = PHONE_SMS;
  form.append(text);

  // 6. Winter
  const winter = el('p', 'est-winter');
  winter.append(
    "Winter services (snow removal and winter cleanups) aren't in the estimator. Call for a quote: ",
    phoneLink(PHONE_TEL, PHONE_DISPLAY),
  );
  form.append(winter);

  function addRow(): Row {
    const id = nextRowId++;
    const wrapper = el('div', 'est-row');
    const label = el('label');
    const input = el('input');
    input.type = 'text';
    input.inputMode = 'decimal';
    input.autocomplete = 'off';
    input.id = `${uid}-diameter-${id}`;
    label.htmlFor = input.id;
    const error = el('p', 'est-error');
    error.id = `${uid}-error-${id}`;
    error.hidden = true;
    const remove = el('button', 'est-btn est-remove', 'Remove');
    remove.type = 'button';
    const controls = el('div', 'est-row-controls');
    controls.append(input, remove);
    wrapper.append(label, controls, error);
    const row: Row = { id, value: '', touched: false, wrapper, label, input, error, remove };
    input.addEventListener('input', () => {
      row.value = input.value;
      row.touched = true;
      update();
    });
    remove.addEventListener('click', () => {
      if (rows.length <= 1) return;
      rows.splice(rows.indexOf(row), 1);
      wrapper.remove();
      update();
    });
    rows.push(row);
    rowsBox.append(wrapper);
    return row;
  }

  function renderResult(res: EstimateResult): void {
    resultBody.textContent = '';
    if (res.kind === 'price') {
      resultBody.append(
        el('p', 'est-result-label', 'Estimated price'),
        el('p', 'est-price', formatRange(res.low, res.high)),
      );
    } else if (res.kind === 'call') {
      const call = el('p', 'est-price');
      call.append(phoneLink(PHONE_TEL, PHONE_DISPLAY));
      resultBody.append(
        el('p', 'est-result-label', 'Call for a quote'),
        call,
      );
    } else if (res.errors.length > 0 && rows.every((r) => r.touched || r.value.trim() !== '')) {
      for (const e of res.errors) {
        resultBody.append(el('p', 'est-result-error', `Check stump ${e.row + 1}: ${e.message}`));
      }
    } else if (rows.some((r) => !r.touched && r.value.trim() === '')) {
      resultBody.append(el('p', undefined, 'Enter a diameter for each stump to see your estimate.'));
    }
  }

  function update(): void {
    rows.forEach((row, i) => {
      row.label.textContent = `Stump ${i + 1} diameter (inches)`;
      row.remove.disabled = rows.length === 1;
    });

    if (restoration.box.checked) {
      cleanup.box.checked = true;
      cleanup.box.disabled = true;
    } else {
      cleanup.box.disabled = false;
    }
    cleanupNote.hidden = !restoration.box.checked;

    for (const q of QUESTIONS) {
      confirmBoxes[q.key].textContent = answers[q.key] === 'not-sure' ? "We'll confirm on-site." : '';
      confirmBoxes[q.key].hidden = answers[q.key] !== 'not-sure';
    }

    const res = estimate({
      diameters: rows.map((r) => r.value),
      cleanup: cleanup.box.checked,
      restoration: restoration.box.checked,
      ...answers,
    });

    const messages = new Map<number, string>();
    if (res.kind === 'error') {
      for (const e of res.errors) messages.set(e.row, e.message);
    }
    rows.forEach((row, i) => {
      const message = messages.get(i);
      const show = message !== undefined && (row.touched || row.value.trim() !== '');
      row.error.textContent = show ? message : '';
      row.error.hidden = !show;
      if (show) {
        row.input.setAttribute('aria-invalid', 'true');
        row.input.setAttribute('aria-describedby', row.error.id);
      } else {
        row.input.removeAttribute('aria-invalid');
        row.input.removeAttribute('aria-describedby');
      }
    });

    renderResult(res);
  }

  addButton.addEventListener('click', () => {
    addRow().input.focus();
    update();
  });
  cleanup.box.addEventListener('change', update);
  restoration.box.addEventListener('change', update);

  addRow();
  update();
}
