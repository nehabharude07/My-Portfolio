// Global entry animations and small UI micro-interactions
(function(){
  document.documentElement.classList.add('js-enabled');
  window.addEventListener('DOMContentLoaded', function(){
    // Fade in main container
    const main = document.querySelector('main.container');
    if(main){
      main.classList.add('fade-in-up');
    }

    // Stagger in project cards if present
    const cards = document.querySelectorAll('.card');
    cards.forEach((c,i)=>{
      c.style.transition = 'transform 400ms ease, opacity 400ms ease';
      c.style.transform = 'translateY(8px)';
      c.style.opacity = '0';
      setTimeout(()=>{ c.style.transform='translateY(0)'; c.style.opacity='1'; }, 120*i);
    });

    // Animate navbar brand subtle pulse to draw attention once
    const brand = document.querySelector('.navbar-brand');
    if(brand){
      brand.animate([{transform:'scale(1)'},{transform:'scale(1.03)'},{transform:'scale(1)'}],{duration:900,iterations:1});
    }
  });
})();
