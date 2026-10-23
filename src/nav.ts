const DESKTOP_QUERY = '(min-width: 768px)';

export function setupNav(root: Document): void {
  const header = root.querySelector<HTMLElement>('.site-header');
  const button = root.querySelector<HTMLButtonElement>('.site-header button[aria-controls]');
  if (!header || !button) return;
  const list = root.getElementById(button.getAttribute('aria-controls') ?? '');
  if (!list) return;

  // The CSS only collapses the list once this attribute is set (progressive enhancement).
  header.setAttribute('data-js', '');

  const setOpen = (open: boolean) => {
    button.setAttribute('aria-expanded', String(open));
    list.classList.toggle('is-open', open);
  };
  const isOpen = () => button.getAttribute('aria-expanded') === 'true';

  button.addEventListener('click', () => {
    const open = !isOpen();
    setOpen(open);
    // The menu precedes the button in DOM order, so hand keyboard focus to its first link.
    if (open) list.querySelector<HTMLElement>('a')?.focus();
  });

  root.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isOpen()) {
      setOpen(false);
      button.focus();
    }
  });

  list.addEventListener('click', (event) => {
    if ((event.target as Element).closest('a')) setOpen(false);
  });

  const view = root.defaultView;
  if (view && typeof view.matchMedia === 'function') {
    view.matchMedia(DESKTOP_QUERY).addEventListener('change', (event) => {
      if (event.matches) setOpen(false);
    });
  }
}
