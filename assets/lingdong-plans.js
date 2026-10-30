(() => {
  const panel = document.getElementById('lingdong-plans');
  if (!panel) return;
  const buttons = [...panel.querySelectorAll('[data-lingdong-filter]')];
  const cards = [...panel.querySelectorAll('[data-lingdong-kind]')];
  const count = panel.querySelector('#lingdong-plan-count');
  const labels = {all:'全部套餐',periodic:'周期套餐',one_time:'不限时流量',custom:'独享定制'};
  function choose(kind) {
    let shown = 0;
    cards.forEach(card => { const visible = kind === 'all' || card.dataset.lingdongKind === kind; card.hidden = !visible; if (visible) shown += 1; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lingdongFilter === kind)));
    count.textContent = `${labels[kind]} · 共${shown}款`;
  }
  buttons.forEach(button => button.addEventListener('click', () => choose(button.dataset.lingdongFilter)));
  document.querySelectorAll('a[href^="#lingdong-plan-"]').forEach(link => link.addEventListener('click', () => {
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target?.hidden) choose('all');
  }));
  document.querySelectorAll('[data-lingdong-show-all]').forEach(link => link.addEventListener('click', () => choose('all')));
})();
