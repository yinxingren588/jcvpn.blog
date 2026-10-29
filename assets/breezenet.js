(() => {
  document.querySelectorAll('[data-breeze-copy]').forEach(button => button.addEventListener('click', async () => {
    const status = button.closest('.breeze-offer').querySelector('.breeze-coupon-status');
    try {
      await navigator.clipboard.writeText(button.dataset.breezeCopy);
      status.textContent = '优惠码已复制，购买时粘贴使用。';
    } catch {
      status.textContent = `请长按或选择优惠码 ${button.dataset.breezeCopy} 手动复制。`;
    }
  }));
  const panel = document.getElementById('breeze-plans');
  if (!panel) return;
  const buttons = [...panel.querySelectorAll('[data-breeze-filter]')];
  const cards = [...panel.querySelectorAll('.breeze-plan')];
  const count = document.getElementById('breeze-plan-count');
  const labels = { all: '全部套餐', year: '年付套餐', month: '月付套餐', once: '一次性流量包' };
  buttons.forEach(button => button.addEventListener('click', () => {
    const choice = button.dataset.breezeFilter;
    let visible = 0;
    cards.forEach(card => {
      const show = choice === 'all' || card.dataset.billing === choice;
      card.hidden = !show;
      if (show) visible += 1;
    });
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    count.textContent = `${labels[choice]} · 共${visible}款`;
  }));
  document.querySelectorAll('a[href^="#breeze-plan-"]').forEach(link => link.addEventListener('click', () => {
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target?.hidden) buttons.find(button => button.dataset.breezeFilter === 'all').click();
  }));
})();
