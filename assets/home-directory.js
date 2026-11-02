(() => {
  const root = document.getElementById('home-directory-root');
  if (!root) return;
  const panel = root.querySelector('.home-directory-panel');
  const launcher = root.querySelector('.home-directory-launcher');
  const close = root.querySelector('.home-directory-close');
  const wide = matchMedia('(min-width: 1800px)');
  const hasPromo = Boolean(document.querySelector('.floating-promo'));
  const links = [...root.querySelectorAll('[data-home-section]')];
  const targets = links.map(link => document.getElementById(link.dataset.homeSection));
  function setOpen(open, focus = false) {
    root.dataset.open = String(open);
    panel.hidden = !open;
    launcher.hidden = open;
    launcher.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('site-directory-expanded', open);
    if (focus) (open ? links[0] : launcher).focus();
  }
  launcher.addEventListener('click', () => setOpen(true, true));
  close.addEventListener('click', () => setOpen(false, true));
  root.addEventListener('keydown', event => {
    if (event.key === 'Escape' && root.dataset.open === 'true') {
      setOpen(false, true);
      event.preventDefault();
    }
  });
  links.forEach((link, index) => link.addEventListener('click', () => {
    if (!wide.matches) {
      setOpen(false);
      const target = targets[index];
      target.tabIndex = -1;
      target.focus({preventScroll: true});
    }
  }));
  function revealSection(link) {
    const target = document.getElementById(link.dataset.homeSection);
    const group = target?.closest('[data-group]');
    if (group && document.querySelector('.faq-item')) {
      const input = document.querySelector('input[type="search"]');
      if (input) { input.value = ''; input.dispatchEvent(new Event('input', {bubbles: true})); }
      const filter = [...document.querySelectorAll('button[data-category]')].find(button => button.dataset.category === group.dataset.group);
      filter?.click();
    }
  }
  links.forEach(link => link.addEventListener('click', () => revealSection(link)));
  function revealHashSection() {
    const link = links.find(item => item.getAttribute('href') === location.hash);
    if (link) revealSection(link);
  }
  addEventListener('hashchange', revealHashSection);
  revealHashSection();
  let scheduled = false;
  function markCurrent() {
    scheduled = false;
    let current = 0;
    targets.forEach((target, index) => {
      if (target && target.getClientRects().length && target.getBoundingClientRect().top <= 160) current = index;
    });
    links.forEach((link, index) => {
      if (index === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(markCurrent); }
  }, {passive: true});
  wide.addEventListener('change', () => { setOpen(wide.matches && !hasPromo); markCurrent(); });
  setOpen(wide.matches && !hasPromo);
  markCurrent();
})();
