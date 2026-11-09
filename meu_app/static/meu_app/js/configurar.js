const qtd = document.getElementById('qtd');
const badge = document.getElementById('valor-disp');
const resumo = document.getElementById('res-disp');

function atualizar() {
  const pct = ((qtd.value - qtd.min) / (qtd.max - qtd.min)) * 100;
  qtd.style.setProperty('--pct', pct + '%');
  badge.textContent = resumo.textContent = qtd.value;
}
qtd.addEventListener('input', atualizar);
atualizar();

// seleção do endpoint
document.querySelectorAll('.endpoint').forEach(ep =>
  ep.addEventListener('click', () => {
    document.querySelectorAll('.endpoint').forEach(o => o.classList.toggle('ativo', o === ep));
  })
);

document.querySelectorAll('[data-scroll]').forEach(btn =>
  btn.addEventListener('click', () => document.querySelector(btn.dataset.scroll)?.scrollIntoView({ behavior: 'smooth' }))
);

// envio do formulário: guarda os dados e segue para o resultado
// (troque por um fetch/POST para o seu backend Django quando tiver a view)
document.getElementById('form-lead').addEventListener('submit', e => {
  e.preventDefault();
  const dados = Object.fromEntries(new FormData(e.target));
  dados.dispositivos = qtd.value;
  dados.endpoint = document.querySelector('.endpoint.ativo')?.dataset.ep || '';
  try { sessionStorage.setItem('bzu_lead', JSON.stringify(dados)); } catch (_) {}
  location.href = document.getElementById('url-resultado').dataset.url;
});
