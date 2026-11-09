// Simula o processamento e segue para o questionário
const status = document.getElementById('status');
let pontos = 0;
const anim = setInterval(() => {
  pontos = (pontos + 1) % 4;
  status.textContent = 'carregando' + '.'.repeat(pontos || 3);
}, 400);
setTimeout(() => { clearInterval(anim); location.href = status.dataset.proxima; }, 3000);
