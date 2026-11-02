(() => {
  const isFaq = Boolean(document.querySelector('.faq-controls'));
  const cards = [...document.querySelectorAll(isFaq ? '.faq-item' : '[data-library-card]')];
  if (!cards.length) return;
  const controls = document.querySelector(isFaq ? '.faq-controls' : '.library-controls');
  const input = controls.querySelector('input[type="search"]');
  const buttons = [...controls.querySelectorAll('button[data-category]')];
  const prefix = isFaq ? 'faq' : 'library';
  const count = document.getElementById(prefix + '-count');
  const current = document.getElementById(prefix + '-page');
  const previous = document.getElementById(prefix + '-previous');
  const next = document.getElementById(prefix + '-next');
  const empty = document.getElementById(prefix + '-empty');
  const size = isFaq ? 20 : 12;
  let category = 'all', page = 1;
  function matches() {
    const query = input.value.trim().toLocaleLowerCase();
    return cards.filter(card => (category === 'all' || card.dataset.category === category) && card.textContent.toLocaleLowerCase().includes(query));
  }
  function render() {
    const found = matches();
    const pages = Math.max(1, Math.ceil(found.length / size));
    page = Math.min(page, pages);
    cards.forEach(card => { card.hidden = true; });
    const shown = found.slice((page - 1) * size, page * size);
    shown.forEach(card => { card.hidden = false; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    if (isFaq) document.querySelectorAll('[data-group]').forEach(group => { group.hidden = ![...group.querySelectorAll('.faq-item')].some(item => !item.hidden); });
    count.textContent = `共${found.length}${isFaq ? '个问题' : '篇文章'}，本页${shown.length}${isFaq ? '个' : '篇'}`;
    current.textContent = `第${page} / ${pages}页`;
    previous.disabled = page === 1;
    next.disabled = page === pages;
    empty.hidden = found.length !== 0;
  }
  buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.category; page = 1; render(); }));
  input.addEventListener('input', () => { page = 1; render(); });
  previous.addEventListener('click', () => { page--; render(); controls.scrollIntoView({block:'start'}); });
  next.addEventListener('click', () => { page++; render(); controls.scrollIntoView({block:'start'}); });
  if (isFaq) {
    document.getElementById('expand-all').addEventListener('click', () => cards.filter(card => !card.hidden).forEach(card => { card.open = true; }));
    document.getElementById('collapse-all').addEventListener('click', () => cards.forEach(card => { card.open = false; }));
    function revealHash() {
      let id;
      try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
      const item = document.getElementById(id);
      if (item?.classList.contains('faq-item')) {
        category = 'all'; input.value = ''; page = Math.floor(cards.indexOf(item) / size) + 1;
        render(); item.open = true; item.scrollIntoView({block:'start'});
      }
    }
    addEventListener('hashchange', revealHash);
    render(); revealHash();
  } else render();
})();
