// Fundo animado de rede (nós + conexões) — cores do protótipo Figma
(() => {
  const c = document.getElementById('bg');
  if (!c) return;
  const ctx = c.getContext('2d');
  const reduzir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let w, h, nos = [];

  function iniciar() {
    const d = devicePixelRatio || 1;
    w = innerWidth; h = innerHeight;
    c.width = w * d; c.height = h * d;
    ctx.setTransform(d, 0, 0, d, 0, 0);
    const n = Math.min(90, Math.floor((w * h) / 16000));
    nos = Array.from({ length: n }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25,
      r: 1.5 + Math.random() * 2.5, p: Math.random() * 6.28,
    }));
  }

  function quadro(t) {
    ctx.clearRect(0, 0, w, h);
    const alcance = 170;
    for (let i = 0; i < nos.length; i++) {
      for (let j = i + 1; j < nos.length; j++) {
        const a = nos[i], b = nos[j], d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < alcance) {
          ctx.strokeStyle = `rgba(122,27,140,${.5 * (1 - d / alcance)})`; // #7A1B8C
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }
    for (const n of nos) {
      const pulso = (Math.sin(t / 900 + n.p) + 1) / 2;
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 6);
      g.addColorStop(0, `rgba(192,75,219,${.35 + .25 * pulso})`);
      g.addColorStop(1, 'rgba(192,75,219,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 6, 0, 6.283); ctx.fill();
      ctx.fillStyle = pulso > .9 ? '#F3D9FA' : '#C04BDB';
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 6.283); ctx.fill();
      if (!reduzir) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
      }
    }
    if (!reduzir) requestAnimationFrame(quadro);
  }

  addEventListener('resize', iniciar);
  iniciar();
  requestAnimationFrame(quadro);
})();
