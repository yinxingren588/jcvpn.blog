(() => {
  document.documentElement.classList.add('chrome-js');
  const menu = document.querySelector('.site-menu');
  const nav = document.querySelector('.site-primary-nav');
  function closeMenu() {
    nav?.classList.remove('is-open');
    menu?.setAttribute('aria-expanded', 'false');
  }
  menu?.addEventListener('click', () => {
    const opened = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(opened));
    nav.classList.toggle('is-open', opened);
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav?.classList.contains('is-open')) {
      closeMenu();
      menu?.focus();
    }
  });
  document.querySelectorAll('[data-copy-contact]').forEach(button => {
    button.addEventListener('click', async () => {
      const value = button.getAttribute('data-copy-contact');
      const status = button.closest('.contact-method').querySelector('.contact-feedback');
      try {
        await navigator.clipboard.writeText(value);
        status.textContent = '已复制：' + value;
      } catch {
        status.textContent = '请手动复制上方显示的联系方式。';
      }
    });
  });
})();
