document.querySelectorAll('[data-scroll]').forEach(btn =>
  btn.addEventListener('click', () => document.querySelector(btn.dataset.scroll)?.scrollIntoView({ behavior: 'smooth' }))
);
