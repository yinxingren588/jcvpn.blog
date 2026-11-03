(() => {
  const panel = document.getElementById('langwang-latency');
  if (!panel) return;
  const cards = [...panel.querySelectorAll('.lat-node')];
  const grid = panel.querySelector('.lat-node-grid');
  const buttons = [...panel.querySelectorAll('[data-langwang-region]')];
  const sort = panel.querySelector('#langwang-lat-sort');
  const status = panel.querySelector('#langwang-lat-status');
  const previous = panel.querySelector('#langwang-lat-prev');
  const next = panel.querySelector('#langwang-lat-next');
  const count = panel.querySelector('#langwang-lat-count');
  const empty = panel.querySelector('.langwang-lat-empty');
  let region = 'all', page = 1;
  const size = 12;
  function render() {
    const filtered = cards.filter(card => (region === 'all' || card.dataset.region === region) && (status.value === 'all' || card.dataset.status === status.value));
    filtered.sort((a, b) => {
      const original = Number(a.dataset.order) - Number(b.dataset.order);
      if (sort.value === 'region') return original;
      if (sort.value === 'source') return Number(a.dataset.sourceOrder) - Number(b.dataset.sourceOrder);
      const av = a.dataset.latency === '' ? null : Number(a.dataset.latency);
      const bv = b.dataset.latency === '' ? null : Number(b.dataset.latency);
      if (av === null && bv === null) return original;
      if (av === null) return 1;
      if (bv === null) return -1;
      return (sort.value === 'ascending' ? av - bv : bv - av) || original;
    });
    const pages = Math.max(1, Math.ceil(filtered.length / size));
    page = Math.min(Math.max(page, 1), pages);
    cards.forEach(card => { card.hidden = true; });
    filtered.slice((page - 1) * size, page * size).forEach(card => { card.hidden = false; grid.append(card); });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.langwangRegion === region)));
    count.textContent = `共${filtered.length}条记录 · 第${page}/${pages}页`;
    empty.hidden = filtered.length !== 0;
    previous.disabled = page === 1;
    next.disabled = page === pages;
  }
  buttons.forEach(button => button.addEventListener('click', () => { region = button.dataset.langwangRegion; page = 1; render(); }));
  sort.addEventListener('change', () => { page = 1; render(); });
  status.addEventListener('change', () => { page = 1; render(); });
  previous.addEventListener('click', () => { page -= 1; render(); });
  next.addEventListener('click', () => { page += 1; render(); });
  render();
})();
