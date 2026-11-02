(() => {
  document.querySelectorAll('[data-flyv-coupon-box]').forEach(box => {
    const input = box.querySelector('input');
    const button = box.querySelector('button');
    const status = box.querySelector('[role="status"]');
    let timer;
    button.addEventListener('click', async () => {
      clearTimeout(timer);
      try {
        await navigator.clipboard.writeText(input.value);
        button.textContent = '已复制';
        status.textContent = '优惠码 fly20 已复制';
      } catch {
        button.textContent = '复制优惠码';
        input.focus();
        input.select();
        status.textContent = '请选中优惠码手动复制';
      }
      timer = setTimeout(() => {
        button.textContent = '复制优惠码';
        status.textContent = '';
      }, 3000);
    });
  });
})();
