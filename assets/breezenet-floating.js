(() => {
  const root = document.getElementById('breezenet-floating-promo');
  if (!root) return;
  const panel = root.querySelector('.fp-panel');
  const launcher = root.querySelector('.fp-launcher');
  const close = root.querySelector('.fp-close');
  const reset = root.querySelector('.fp-reset');
  const handle = root.querySelector('.fp-handle');
  const copy = root.querySelector('.fp-copy');
  const input = root.querySelector('.fp-coupon input');
  const status = root.querySelector('.fp-copy-status');
  const desktop = window.matchMedia('(min-width:1100px)');
  let positioned = false, drag = null, copyTimer;
  const clamp = (value, min, max) => Math.min(Math.max(value, min), Math.max(min, max));
  function resetPosition() {
    root.style.removeProperty('left');
    root.style.removeProperty('top');
    root.style.removeProperty('bottom');
    positioned = false;
  }
  function setOpen(open, focus = false) {
    root.dataset.open = String(open);
    panel.hidden = !open;
    launcher.hidden = open;
    launcher.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('promo-expanded', open && desktop.matches);
    if (!open) resetPosition();
    if (focus) (open ? close : launcher).focus();
  }
  function keepInView() {
    if (!positioned || root.dataset.open !== 'true') return;
    const rect = root.getBoundingClientRect();
    root.style.left = clamp(rect.left, 10, innerWidth - rect.width - 10) + 'px';
    root.style.top = clamp(rect.top, 10, innerHeight - rect.height - 10) + 'px';
  }
  setOpen(desktop.matches);
  close.addEventListener('click', () => setOpen(false, true));
  launcher.addEventListener('click', () => setOpen(true, true));
  reset.addEventListener('click', resetPosition);
  root.addEventListener('keydown', event => {
    if (event.key === 'Escape' && root.dataset.open === 'true') {
      event.preventDefault();
      setOpen(false, true);
    }
  });
  desktop.addEventListener('change', event => { resetPosition(); setOpen(event.matches); });
  window.addEventListener('resize', keepInView);
  handle.addEventListener('pointerdown', event => {
    if (event.button !== 0 || event.target.closest('button,a')) return;
    const rect = root.getBoundingClientRect();
    drag = { id: event.pointerId, dx: event.clientX - rect.left, dy: event.clientY - rect.top };
    root.style.left = rect.left + 'px';
    root.style.top = rect.top + 'px';
    root.style.bottom = 'auto';
    positioned = true;
    root.classList.add('is-dragging');
    handle.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  handle.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return;
    const rect = root.getBoundingClientRect();
    root.style.left = clamp(event.clientX - drag.dx, 10, innerWidth - rect.width - 10) + 'px';
    root.style.top = clamp(event.clientY - drag.dy, 10, innerHeight - rect.height - 10) + 'px';
  });
  function endDrag(event) {
    if (!drag || drag.id !== event.pointerId) return;
    drag = null;
    root.classList.remove('is-dragging');
    if (handle.hasPointerCapture(event.pointerId)) handle.releasePointerCapture(event.pointerId);
  }
  handle.addEventListener('pointerup', endDrag);
  handle.addEventListener('pointercancel', endDrag);
  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(input.value);
      copy.textContent = '已复制';
      status.textContent = '优惠码 ' + input.value + ' 已复制';
    } catch {
      input.focus(); input.select();
      status.textContent = '请选中优惠码复制';
    }
    clearTimeout(copyTimer);
    copyTimer = setTimeout(() => { copy.textContent = '复制'; status.textContent = ''; }, 2200);
  });
})();
