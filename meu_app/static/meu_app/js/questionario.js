const opcoes = [...document.querySelectorAll('.opcao')];

function marcar(op) {
  opcoes.forEach(o => o.setAttribute('aria-checked', String(o === op)));
  try { sessionStorage.setItem('bzu_coleta', op.dataset.valor); } catch (_) {}
}

opcoes.forEach(op => op.addEventListener('click', () => marcar(op)));

// restaura a resposta anterior
try {
  const salva = sessionStorage.getItem('bzu_coleta');
  const op = opcoes.find(o => o.dataset.valor === salva);
  if (op) marcar(op);
} catch (_) {}
