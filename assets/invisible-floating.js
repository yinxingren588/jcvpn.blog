(()=>{
 const root=document.getElementById('invisible-floating-promo');if(!root)return;
 const panel=root.querySelector('.fp-panel'),launcher=root.querySelector('.fp-launcher'),close=root.querySelector('.fp-close'),reset=root.querySelector('.fp-reset'),handle=root.querySelector('.fp-handle'),copy=root.querySelector('.fp-copy'),input=root.querySelector('#floating-coupon-code'),status=root.querySelector('.fp-copy-status');
 const desktop=window.matchMedia('(min-width:1100px)');let positioned=false,drag=null,copyTimer;
 const clamp=(value,min,max)=>Math.min(Math.max(value,min),Math.max(min,max));
 function resetPosition(){root.style.removeProperty('left');root.style.removeProperty('top');root.style.removeProperty('bottom');positioned=false;}
 function setOpen(open,focus=false){root.dataset.open=String(open);panel.hidden=!open;launcher.hidden=open;launcher.setAttribute('aria-expanded',String(open));document.body.classList.toggle('promo-expanded',open&&desktop.matches);if(!open)resetPosition();if(focus)(open?close:launcher).focus();}
 function keepInView(){if(!positioned||root.dataset.open!=='true')return;const r=root.getBoundingClientRect();root.style.left=clamp(r.left,10,innerWidth-r.width-10)+'px';root.style.top=clamp(r.top,10,innerHeight-r.height-10)+'px';}
 setOpen(desktop.matches);
 close.addEventListener('click',()=>setOpen(false,true));launcher.addEventListener('click',()=>setOpen(true,true));reset.addEventListener('click',resetPosition);
 root.addEventListener('keydown',event=>{if(event.key==='Escape'&&root.dataset.open==='true'){event.preventDefault();setOpen(false,true);}});
 desktop.addEventListener('change',event=>{resetPosition();setOpen(event.matches);});window.addEventListener('resize',keepInView);
 handle.addEventListener('pointerdown',event=>{if(event.button!==0||event.target.closest('button,a'))return;const r=root.getBoundingClientRect();drag={id:event.pointerId,dx:event.clientX-r.left,dy:event.clientY-r.top};root.style.left=r.left+'px';root.style.top=r.top+'px';root.style.bottom='auto';positioned=true;root.classList.add('is-dragging');handle.setPointerCapture(event.pointerId);event.preventDefault();});
 handle.addEventListener('pointermove',event=>{if(!drag||drag.id!==event.pointerId)return;const r=root.getBoundingClientRect();root.style.left=clamp(event.clientX-drag.dx,10,innerWidth-r.width-10)+'px';root.style.top=clamp(event.clientY-drag.dy,10,innerHeight-r.height-10)+'px';});
 function endDrag(event){if(!drag||drag.id!==event.pointerId)return;drag=null;root.classList.remove('is-dragging');if(handle.hasPointerCapture(event.pointerId))handle.releasePointerCapture(event.pointerId);}
 handle.addEventListener('pointerup',endDrag);handle.addEventListener('pointercancel',endDrag);
 copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(input.value);copy.textContent='已复制';status.textContent='优惠码 '+input.value+' 已复制';}catch{input.focus();input.select();copy.textContent='复制';status.textContent='请选中优惠码复制';}clearTimeout(copyTimer);copyTimer=setTimeout(()=>{copy.textContent='复制';status.textContent='';},2200);});
})();
