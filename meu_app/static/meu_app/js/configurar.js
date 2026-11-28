// Página de resultado. Enquanto a simulação está pendente, chama a API que roda
// as regras + IA (pode levar até ~1 min) e recarrega a página quando termina.
const aguardando = document.getElementById('aguardando');

if (aguardando) {
  const status = document.getElementById('status-simulacao');
  const erro = document.getElementById('erro-carregando');
  const tentar = document.getElementById('tentar-novamente');
  const token = aguardando.querySelector('[name=csrfmiddlewaretoken]').value;
  const INTERVALO_MS = 4000;     // se outra aba já está processando, pergunta de novo a cada 4 s
  const LIMITE_MS = 3 * 60000;   // desiste depois de 3 min e oferece "Tentar novamente"
  let inicio = Date.now();

  // reticências animadas no título
  let pontos = 0;
  setInterval(() => {
    pontos = (pontos + 1) % 4;
    status.textContent = 'Analisando sua operação' + '.'.repeat(pontos || 3);
  }, 500);

  function mostrarErro(mensagem) {
    erro.textContent = mensagem;
    erro.hidden = false;
    tentar.hidden = false;
  }

  async function executar() {
    erro.hidden = true;
    tentar.hidden = true;
    try {
      const resp = await fetch(aguardando.dataset.api, {
        method: 'POST',
        headers: { 'X-CSRFToken': token },
      });
      const dados = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(dados.erro || 'Não foi possível processar a simulação.');

      if (dados.status === 'processando') {
        if (Date.now() - inicio > LIMITE_MS) {
          mostrarErro('A análise está demorando mais que o normal.');
          return;
        }
        setTimeout(executar, INTERVALO_MS);
        return;
      }
      window.location.reload(); // pronta ou erro: o servidor desenha o resultado
    } catch (e) {
      mostrarErro(e instanceof TypeError ? 'Sem conexão com o servidor.' : e.message);
    }
  }

  tentar.addEventListener('click', () => { inicio = Date.now(); executar(); });
  executar();
}
