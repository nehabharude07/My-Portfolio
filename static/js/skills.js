/* Animate skill progress bars and numeric counters when visible */
(function(){
  const bars = Array.from(document.querySelectorAll('.skill-bar'));
  if(!bars.length) return;

  function animateBar(bar){
    const target = parseInt(bar.dataset.target || '0',10);
    bar.style.width = target + '%';
    const parent = bar.closest('.skill');
    const valueEl = parent.querySelector('.skill-value');
    // animate number
    let start = 0;
    const duration = 1100;
    const startTime = performance.now();
    function tick(now){
      const t = Math.min(1, (now - startTime) / duration);
      const current = Math.round(t * target);
      valueEl.textContent = current + '%';
      if(t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        const bar = entry.target;
        if(!bar.classList.contains('animated')){
          bar.classList.add('animated');
          animateBar(bar);
        }
      }
    });
  }, {threshold: 0.4});

  bars.forEach(b => observer.observe(b));
})();
