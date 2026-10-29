(() => {
  const panel = document.getElementById('twilight-plans');
  if (!panel) return;
  const buttons = [...panel.querySelectorAll('[data-twilight-filter]')];
  const cards = [...panel.querySelectorAll('[data-twilight-kind]')];
  const count = panel.querySelector('#twilight-plan-count');
  const labels = {all:'全部套餐',periodic:'周期套餐',one_time:'不限时流量',custom:'独享定制'};
  function choose(kind) {
    let shown = 0;
    cards.forEach(card => { const visible = kind === 'all' || card.dataset.twilightKind === kind; card.hidden = !visible; if (visible) shown += 1; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.twilightFilter === kind)));
    count.textContent = `${labels[kind]} · 共${shown}款`;
  }
  buttons.forEach(button => button.addEventListener('click', () => choose(button.dataset.twilightFilter)));
  document.querySelectorAll('a[href^="#twilight-plan-"]').forEach(link => link.addEventListener('click', () => {
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target?.hidden) choose('all');
  }));
  document.querySelectorAll('[data-twilight-show-all]').forEach(link => link.addEventListener('click', () => choose('all')));
})();
