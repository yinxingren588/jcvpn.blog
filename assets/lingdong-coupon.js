(() => {
  document.querySelectorAll('[data-lingdong-coupon-box]').forEach(box => {
    const input = box.querySelector('input');
    const button = box.querySelector('button');
    const status = box.querySelector('.lingdong-copy-status');
    let timer;
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(input.value);
        button.textContent = '已复制';
        status.textContent = '优惠码已复制';
      } catch {
        input.focus();
        input.select();
        status.textContent = '请选中优惠码复制';
      }
      clearTimeout(timer);
      timer = setTimeout(() => { button.textContent = '复制'; status.textContent = ''; }, 2400);
    });
  });
})();
