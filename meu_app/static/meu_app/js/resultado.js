// clicar em um indicador rola até o detalhamento correspondente
document.querySelectorAll('[data-alvo]').forEach(btn =>
  btn.addEventListener('click', () =>
    document.querySelector(btn.dataset.alvo)?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
);
