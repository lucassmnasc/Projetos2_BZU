// Questionário do Simulador Bzu: perguntas 2 a 19 (a pergunta 1 é a criação da conta).
// Cada pergunta é descrita em PERGUNTAS e desenhada no cartão #pergunta, uma por vez.

const CHAVE_ESTADO = 'bzu_questionario';
const LIMITE_OUTRO = 150;
const LIMITE_TEXTO = 500;

const BLOCOS = {
  perfil: 'Bloco 1 · Perfil da empresa',
  operacao: 'Bloco 2 · Mapeamento da operação',
  diagnostico: 'Bloco 3 · Diagnóstico específico',
};

const SETORES = {
  energia: 'Consumo e qualidade de energia elétrica',
  temperatura: 'Temperatura e umidade',
  ar: 'Qualidade do ar',
  pressao: 'Pressão diferencial',
  portas: 'Abertura e fechamento de portas e janelas',
  luminosidade: 'Luminosidade',
  gases: 'Concentração de gases e partículas no ar',
  maquinas: 'Máquinas e equipamentos',
  outras: 'Outras variáveis de monitoramento',
};

const AMBIENTES_FRIO = [
  ['camaras-frias', 'Câmaras frias.'],
  ['freezers', 'Freezers e refrigeradores.'],
  ['armazenamento', 'Ambientes de armazenamento.'],
  ['producao', 'Salas de produção.'],
  ['trabalho', 'Ambientes de trabalho.'],
  ['estufas', 'Estufas e ambientes agrícolas.'],
];

const outro = (rotulo = 'Outro.', label = 'Descreva') => ({ valor: 'outro', rotulo, label });

const PERGUNTAS = {
  // ---------------------------------------------------------- Bloco 1
  segmento: {
    bloco: 'perfil', numero: '2', tipo: 'multipla',
    titulo: 'Em qual segmento sua empresa atua?',
    opcoes: [
      ['industria-manufatura', 'Indústria e manufatura'],
      ['energia-utilities', 'Energia e utilities'],
      ['varejo-comercio', 'Varejo e comércio'],
      ['logistica-transporte', 'Logística e transporte'],
      ['agronegocio', 'Agronegócio'],
      ['saude-medicina', 'Saúde e medicina'],
      ['alimentacao-cadeia-fria', 'Alimentação e cadeia fria'],
      ['edificios-instalacoes', 'Edifícios e instalações'],
      ['telecomunicacoes', 'Telecomunicações'],
      ['cidades-setor-publico', 'Cidades e setor público'],
      ['educacao', 'Educação'],
    ],
    outro: outro('Outros serviços e operações', 'Descreva o segmento da sua empresa'),
  },
  'conhece-iot': {
    bloco: 'perfil', numero: '3', tipo: 'unica',
    titulo: 'Você já ouviu falar em IoT?',
    opcoes: [
      ['sim', 'Sim'],
      ['nao', 'Não'],
      ['ja-ouvi', 'Já ouvi falar, mas não sei exatamente como funciona.'],
    ],
    explicacao: ['nao', 'ja-ouvi'],
  },
  'usa-iot': {
    bloco: 'perfil', numero: '4', tipo: 'unica',
    titulo: 'Vocês já utilizam alguma solução de IoT para monitorar o funcionamento da sua operação?',
    opcoes: [['sim', 'Sim'], ['nao', 'Não']],
  },
  'uso-iot': {
    bloco: 'perfil', numero: '4.1', tipo: 'unica',
    titulo: 'Como você utiliza o monitoramento por IoT em sua operação?',
    opcoes: [
      ['frequente', 'Temos controle e acompanhamento frequente.'],
      ['periodico', 'Realizamos verificações periódicas, mas não continuamente.'],
      ['manual', 'Dependemos de verificações manuais dos funcionários.'],
      ['sem-central', 'Possuímos equipamentos de medição, mas sem acompanhamento centralizado.'],
      ['ja-iot', 'Já utilizamos sistemas de monitoramento por IoT.'],
      ['nenhum', 'Não realizamos nenhum tipo de monitoramento.'],
      ['nao-sei', 'Não sei informar.'],
    ],
  },
  porte: {
    bloco: 'perfil', numero: '5', tipo: 'unica',
    titulo: 'Qual é o porte da empresa?',
    instrucao: 'De acordo com a receita bruta anual. Classificação do BNDES.',
    opcoes: [
      ['micro', 'Microempresa (até R$ 360 mil/ano)'],
      ['pequena', 'Pequena empresa (acima de R$ 360 mil até R$ 4,8 milhões/ano)'],
      ['media', 'Média empresa (acima de R$ 4,8 milhões até R$ 300 milhões/ano)'],
      ['grande', 'Grande empresa (acima de R$ 300 milhões/ano)'],
    ],
  },
  unidades: {
    bloco: 'perfil', numero: '6', tipo: 'unica',
    titulo: 'Quantas unidades ou estabelecimentos sua empresa possui?',
    opcoes: [
      ['1', '1 unidade'], ['2-5', '2 a 5 unidades'], ['6-10', '6 a 10 unidades'],
      ['11-20', '11 a 20 unidades'], ['21-50', '21 a 50 unidades'], ['51-100', '51 a 100 unidades'],
      ['101-500', '101 a 500 unidades'], ['500+', '+500 unidades'],
    ],
  },

  // ---------------------------------------------------------- Bloco 2
  horario: {
    bloco: 'operacao', numero: '7', tipo: 'colunas',
    titulo: 'Como funciona o horário de operação da empresa?',
    instrucao: 'Marque uma opção em cada coluna.',
    colunas: [
      {
        chave: 'dias', titulo: 'Dias',
        opcoes: [
          ['seg-sex', 'Segunda a sexta-feira'],
          ['seg-sab', 'Segunda a sábado'],
          ['seg-dom', 'Segunda a domingo'],
          ['todos', 'Todos os dias, inclusive feriados'],
          ['variaveis', 'Dias variáveis, conforme demanda'],
        ],
      },
      {
        chave: 'horario', titulo: 'Horário',
        opcoes: [
          ['comercial', 'Horário comercial, aproximadamente das 8h às 18h'],
          ['estendido', 'Horário estendido, aproximadamente das 7h às 22h'],
          ['continuo', 'Funcionamento contínuo, 24 horas por dia'],
        ],
        outro: outro('Outro', 'Descreva o horário de operação'),
      },
    ],
  },
  setor: {
    bloco: 'operacao', numero: '8', tipo: 'multipla',
    titulo: 'Qual setor da sua operação você gostaria de analisar a implementação de IoT?',
    opcoes: [
      ['energia', 'Consumo e qualidade de energia elétrica'],
      ['temperatura', 'Temperatura e umidade'],
      ['ar', 'Qualidade do ar'],
      ['pressao', 'Pressão diferencial (pressão entre ambientes)'],
      ['portas', 'Abertura e fechamento de portas e janelas'],
      ['luminosidade', 'Luminosidade'],
      ['gases', 'Concentração de gases e partículas no ar'],
      ['maquinas', 'Máquinas e equipamentos'],
      ['nao-sei', 'Não sei, quero descobrir onde a IoT pode ajudar minha empresa'],
    ],
    exclusiva: 'nao-sei',
    outro: {
      valor: 'outras', rotulo: 'Outras variáveis de monitoramento', area: true,
      label: 'Descreva o que você gostaria de monitorar em sua operação. Caso não saiba exatamente qual variável precisa medir, explique o problema que deseja resolver…',
    },
  },
  situacoes: {
    bloco: 'operacao', numero: '8.1', tipo: 'multipla',
    titulo: 'Quais situações você gostaria de melhorar na sua operação?',
    opcoes: [
      ['energia', 'Gastos elevados com energia elétrica'],
      ['desperdicio', 'Desperdício de produtos ou matérias-primas'],
      ['temperatura', 'Alterações de temperatura em ambientes ou equipamentos'],
      ['ar', 'Problemas relacionados à qualidade do ar'],
      ['falhas', 'Falhas ou funcionamento inadequado de equipamentos'],
      ['ambientes', 'Dificuldade de controlar as condições dos ambientes'],
      ['portas', 'Portas ou janelas que ficam abertas indevidamente'],
      ['informacao', 'Falta de informações sobre o funcionamento da operação'],
      ['condicoes', 'Necessidade de acompanhar condições ambientais'],
    ],
    outro: outro('Outro', 'Descreva a situação'),
  },
  prioridade: {
    bloco: 'operacao', numero: '8.2', tipo: 'unica',
    titulo: 'Qual dessas operações você deseja analisar primeiro?',
    opcoes: [], // preenchidas a partir das respostas 8 ou 8.1
  },

  // ---------------------------------------------------------- Bloco 3
  funcionarios: {
    bloco: 'diagnostico', numero: '9', tipo: 'unica',
    titulo: 'Quantos funcionários trabalham nessa operação?',
    opcoes: [
      ['1-5', '1 a 5 funcionários'], ['6-20', '6 a 20 funcionários'], ['21-50', '21 a 50 funcionários'],
      ['51-100', '51 a 100 funcionários'], ['101-250', '101 a 250 funcionários'],
      ['251-500', '251 a 500 funcionários'], ['501-1000', '501 a 1000 funcionários'],
      ['1000+', '+1000 funcionários'],
    ],
  },
  // Pergunta 10 (o PDF pula do 9 para o 11): base do dimensionamento por área em calculos.py
  area: {
    bloco: 'diagnostico', numero: '10', tipo: 'numero', unidade: 'm²', maximo: 1000000,
    titulo: 'Qual é a área aproximada, em m², dos ambientes que serão monitorados?',
    instrucao: 'Some a área de todos os ambientes do setor que será analisado. Uma estimativa já ajuda.',
  },

  // 1. Energia
  'energia-equipamentos': {
    bloco: 'diagnostico', numero: '11.1', tipo: 'texto',
    titulo: 'Quais equipamentos representam os maiores gastos com energia elétrica?',
    placeholder: 'Ex.: compressores, ar-condicionado central, fornos...',
  },
  'energia-conta': {
    bloco: 'diagnostico', numero: '11.2', tipo: 'moeda',
    titulo: 'Qual é o valor médio mensal da conta de energia elétrica da operação analisada?',
  },
  'energia-dificuldade': {
    bloco: 'diagnostico', numero: '11.3', tipo: 'texto',
    titulo: 'Qual é a sua principal dificuldade em relação ao consumo de energia?',
    placeholder: 'Ex.: não sabemos quais equipamentos consomem mais, picos de demanda...',
  },
  'energia-setores': {
    bloco: 'diagnostico', numero: '11.4', tipo: 'multipla',
    titulo: 'Nesse setor, quais equipamentos representam os maiores gastos com energia elétrica?',
    opcoes: AMBIENTES_FRIO,
    outro: outro('Outros'),
  },

  // 2. Temperatura e umidade
  'temperatura-ambientes': {
    bloco: 'diagnostico', numero: '12.1', tipo: 'multipla',
    titulo: 'Quais ambientes ou equipamentos precisam de controle de temperatura e umidade?',
    opcoes: AMBIENTES_FRIO,
    outro: outro('Outros'),
  },
  'temperatura-finalidade': {
    bloco: 'diagnostico', numero: '12.2', tipo: 'unica',
    titulo: 'Qual é a principal finalidade desse monitoramento?',
    opcoes: [
      ['alteracoes', 'Evitar alterações inadequadas de temperatura.'],
      ['perdas', 'Evitar perdas de produtos armazenados.'],
      ['conservacao', 'Garantir condições adequadas de conservação.'],
      ['ambientais', 'Acompanhar condições ambientais.'],
      ['conformidade', 'Atender exigências de controle e conformidade.'],
    ],
    outro: outro('Outra'),
  },

  // 3. Qualidade do ar
  'ar-variaveis': {
    bloco: 'diagnostico', numero: '13.1', tipo: 'multipla',
    titulo: 'O que você gostaria de acompanhar na qualidade do ar dos ambientes?',
    opcoes: [
      ['eco2', 'Concentração de CO₂ equivalente.'],
      ['voc', 'Presença de gases e compostos orgânicos voláteis.'],
      ['particulas', 'Concentração de partículas suspensas.'],
      ['geral', 'Condições gerais da qualidade do ar.'],
    ],
    outro: outro('Outros'),
  },
  'ar-ambientes': {
    bloco: 'diagnostico', numero: '13.2', tipo: 'multipla',
    titulo: 'Em quais ambientes você deseja realizar esse monitoramento?',
    opcoes: [
      ['trabalho', 'Salas de trabalho.'],
      ['aula', 'Salas de aula.'],
      ['comerciais', 'Ambientes comerciais.'],
      ['industriais', 'Ambientes industriais.'],
      ['saude', 'Hospitais e clínicas.'],
      ['armazenamento', 'Áreas de armazenamento.'],
    ],
    outro: outro('Outros'),
  },
  'ar-finalidade': {
    bloco: 'diagnostico', numero: '13.3', tipo: 'unica',
    titulo: 'Qual é a finalidade desse monitoramento?',
    opcoes: [
      ['melhorar', 'Melhorar as condições ambientais.'],
      ['alteracoes', 'Identificar alterações na qualidade do ar.'],
      ['fontes', 'Investigar possíveis fontes de poluentes.'],
      ['ventilacao', 'Acompanhar a ventilação dos ambientes.'],
      ['requisitos', 'Atender requisitos de controle ambiental.'],
    ],
    outro: outro(),
  },

  // 4. Pressão diferencial
  'pressao-ambientes': {
    bloco: 'diagnostico', numero: '14.1', tipo: 'multipla',
    titulo: 'Em quais ambientes ou sistemas você precisa acompanhar a diferença de pressão?',
    opcoes: [
      ['salas-limpas', 'Salas limpas.'],
      ['hospitalares', 'Ambientes hospitalares.'],
      ['laboratorios', 'Laboratórios.'],
      ['industriais', 'Ambientes industriais.'],
      ['ventilacao', 'Sistemas de ventilação e filtragem.'],
    ],
    outro: outro(),
  },
  'pressao-finalidade': {
    bloco: 'diagnostico', numero: '14.2', tipo: 'unica',
    titulo: 'Qual é a principal finalidade desse monitoramento?',
    opcoes: [
      ['garantir', 'Garantir diferenças de pressão entre ambientes.'],
      ['ventilacao', 'Acompanhar condições de sistemas de ventilação.'],
      ['alteracoes', 'Identificar alterações nas condições de pressurização.'],
      ['controle', 'Verificar condições de controle ambiental.'],
    ],
    outro: outro(),
  },

  // 5. Portas e janelas
  'portas-estruturas': {
    bloco: 'diagnostico', numero: '15.1', tipo: 'multipla',
    titulo: 'Quais estruturas você gostaria de monitorar?',
    opcoes: [
      ['camaras-frias', 'Portas de câmaras frias.'],
      ['armazenamento', 'Portas de ambientes de armazenamento.'],
      ['restrito', 'Portas de acesso restrito.'],
      ['comuns', 'Portas comuns.'],
      ['janelas', 'Janelas.'],
    ],
    outro: outro(),
  },
  'portas-motivo': {
    bloco: 'diagnostico', numero: '15.2', tipo: 'unica',
    titulo: 'Qual é o principal motivo desse monitoramento?',
    opcoes: [
      ['indevidas', 'Identificar portas abertas indevidamente.'],
      ['tempo', 'Controlar o tempo em que permanecem abertas.'],
      ['ambientais', 'Evitar alterações nas condições ambientais.'],
      ['acessos', 'Acompanhar acessos e movimentações.'],
    ],
    outro: outro(),
  },

  // 6. Luminosidade
  'luminosidade-ambientes': {
    bloco: 'diagnostico', numero: '16.1', tipo: 'multipla',
    titulo: 'Em quais ambientes você gostaria de monitorar a luminosidade?',
    opcoes: [
      ['trabalho', 'Ambientes de trabalho.'],
      ['producao', 'Áreas de produção.'],
      ['armazenamento', 'Ambientes de armazenamento.'],
      ['estufas', 'Estufas e ambientes agrícolas.'],
      ['comerciais', 'Ambientes comerciais.'],
    ],
    outro: outro(),
  },
  'luminosidade-motivo': {
    bloco: 'diagnostico', numero: '16.2', tipo: 'unica',
    titulo: 'Qual é o principal motivo desse monitoramento?',
    opcoes: [
      ['niveis', 'Acompanhar os níveis de iluminação.'],
      ['variacoes', 'Identificar variações na luminosidade.'],
      ['condicoes', 'Avaliar as condições de iluminação dos ambientes.'],
    ],
    outro: outro(),
  },

  // 7. Gases e partículas
  'gases-ambientes': {
    bloco: 'diagnostico', numero: '17.1', tipo: 'multipla',
    titulo: 'Em quais ambientes você gostaria de monitorar a concentração de gases e partículas?',
    opcoes: [
      ['industriais', 'Ambientes industriais e áreas de produção.'],
      ['escritorios', 'Salas de trabalho e escritórios.'],
      ['escolares', 'Salas de aula e ambientes escolares.'],
      ['saude', 'Hospitais, clínicas e laboratórios.'],
      ['comerciais', 'Ambientes comerciais.'],
      ['estoques', 'Estoques e áreas de armazenamento.'],
      ['pouca-ventilacao', 'Ambientes fechados com pouca ventilação.'],
    ],
    outro: outro(),
  },
  'gases-substancias': {
    bloco: 'diagnostico', numero: '17.2', tipo: 'multipla',
    titulo: 'Quais substâncias ou partículas você gostaria de monitorar?',
    opcoes: [
      ['eco2', 'CO₂ equivalente (eCO₂).'],
      ['tvoc', 'Compostos orgânicos voláteis (TVOC).'],
      ['pm-finas', 'Partículas finas (PM1.0 e PM2.5).'],
      ['pm-suspensas', 'Partículas suspensas (PM4.0 e PM10).'],
    ],
    outro: outro(),
  },
  'gases-objetivo': {
    bloco: 'diagnostico', numero: '17.3', tipo: 'unica',
    titulo: 'Qual é o principal objetivo desse monitoramento?',
    opcoes: [
      ['alteracoes', 'Identificar alterações na qualidade do ar.'],
      ['fontes', 'Investigar possíveis fontes de poluentes.'],
      ['ventilacao', 'Acompanhar as condições de ventilação dos ambientes.'],
      ['qualidade', 'Identificar situações que possam comprometer a qualidade ambiental.'],
      ['emissoes', 'Monitorar possíveis emissões de gases e partículas.'],
      ['requisitos', 'Atender requisitos de controle ambiental.'],
    ],
    outro: outro(),
  },

  // 8. Máquinas e equipamentos
  'maquinas-tipos': {
    bloco: 'diagnostico', numero: '18.1', tipo: 'multipla',
    titulo: 'Que tipo de máquinas ou equipamentos você gostaria de monitorar?',
    opcoes: [
      ['producao', 'Máquinas de produção industrial.'],
      ['refrigeracao', 'Equipamentos de refrigeração (freezers, câmaras frias e refrigeradores).'],
      ['climatizacao', 'Sistemas de climatização e ar-condicionado.'],
      ['motores', 'Motores e equipamentos elétricos.'],
      ['bombas', 'Bombas e sistemas de bombeamento.'],
      ['ventilacao', 'Equipamentos de ventilação.'],
    ],
    outro: outro(),
  },
  'maquinas-variaveis': {
    bloco: 'diagnostico', numero: '18.2', tipo: 'multipla',
    titulo: 'O que você gostaria de acompanhar nesses equipamentos?',
    opcoes: [
      ['energia', 'Consumo de energia elétrica.'],
      ['temperatura', 'Temperatura de funcionamento.'],
      ['umidade', 'Condições de umidade no ambiente.'],
      ['ar', 'Condições de qualidade do ar ao redor dos equipamentos.'],
      ['pressao', 'Pressão diferencial em sistemas associados.'],
    ],
    outro: outro(),
  },
  'maquinas-quantidade': {
    bloco: 'diagnostico', numero: '18.3', tipo: 'unica',
    titulo: 'Quantos equipamentos você gostaria de monitorar?',
    opcoes: [
      ['1', '1'], ['2-5', '2 a 5'], ['6-10', '6 a 10'], ['11-20', '11 a 20'],
      ['21-50', '21 a 50'], ['51-100', '51 a 100'], ['100+', '+100'],
    ],
  },
  'maquinas-objetivo': {
    bloco: 'diagnostico', numero: '18.4', tipo: 'unica',
    titulo: 'Qual é o principal objetivo desse monitoramento?',
    opcoes: [
      ['consumo', 'Identificar equipamentos que consomem mais energia.'],
      ['alteracoes', 'Identificar alterações nas condições de funcionamento.'],
      ['desempenho', 'Acompanhar o desempenho dos equipamentos.'],
      ['desperdicios', 'Identificar possíveis desperdícios.'],
      ['falhas', 'Evitar perdas relacionadas a falhas operacionais.'],
      ['controle', 'Melhorar o controle da operação.'],
    ],
    outro: outro(),
  },

  // 9. Outras variáveis
  'outras-local': {
    bloco: 'diagnostico', numero: '19.1', tipo: 'texto',
    titulo: 'Em qual ambiente, equipamento ou processo essa necessidade está presente?',
    placeholder: 'Ex.: linha de envase, depósito de insumos...',
  },
  'outras-problema': {
    bloco: 'diagnostico', numero: '19.2', tipo: 'texto',
    titulo: 'Qual problema ou dificuldade você pretende solucionar com esse monitoramento?',
    placeholder: 'Descreva o problema que você quer resolver.',
  },
};

const PERGUNTAS_POR_SETOR = {
  energia: ['energia-equipamentos', 'energia-conta', 'energia-dificuldade', 'energia-setores'],
  temperatura: ['temperatura-ambientes', 'temperatura-finalidade'],
  ar: ['ar-variaveis', 'ar-ambientes', 'ar-finalidade'],
  pressao: ['pressao-ambientes', 'pressao-finalidade'],
  portas: ['portas-estruturas', 'portas-motivo'],
  luminosidade: ['luminosidade-ambientes', 'luminosidade-motivo'],
  gases: ['gases-ambientes', 'gases-substancias', 'gases-objetivo'],
  maquinas: ['maquinas-tipos', 'maquinas-variaveis', 'maquinas-quantidade', 'maquinas-objetivo'],
  outras: ['outras-local', 'outras-problema'],
};

// Pergunta 8.1: cada situação aponta para os setores em que os sensores da Bzu ajudam.
const SITUACAO_PARA_SETORES = {
  energia: ['energia', 'maquinas'],
  desperdicio: ['temperatura', 'maquinas'],
  temperatura: ['temperatura'],
  ar: ['ar', 'gases'],
  falhas: ['maquinas'],
  ambientes: ['temperatura', 'ar'],
  portas: ['portas'],
  informacao: ['maquinas', 'energia'],
  condicoes: ['temperatura', 'luminosidade'],
  outro: ['outras'],
};

const TOTAL_ESTIMADO = 14; // perguntas em um caminho típico, usado só na barra de progresso

// ------------------------------------------------------------------ estado

const el = {
  bloco: document.getElementById('bloco-pergunta'),
  numero: document.getElementById('numero-pergunta'),
  barra: document.getElementById('barra-progresso'),
  titulo: document.getElementById('titulo-pergunta'),
  instrucao: document.getElementById('instrucao-pergunta'),
  corpo: document.getElementById('corpo-pergunta'),
  anterior: document.getElementById('pergunta-anterior'),
  proxima: document.getElementById('proxima-pergunta'),
};

let estado = { historico: ['segmento'], respostas: {} };

function salvar() {
  try { sessionStorage.setItem(CHAVE_ESTADO, JSON.stringify(estado)); } catch (_) {}
}

function carregar() {
  try {
    const salvo = JSON.parse(sessionStorage.getItem(CHAVE_ESTADO) || 'null');
    if (salvo && Array.isArray(salvo.historico) && salvo.historico.length
        && salvo.historico.every((id) => PERGUNTAS[id]) && salvo.respostas) {
      estado = salvo;
    }
  } catch (_) {}
}

const atual = () => estado.historico[estado.historico.length - 1];
const resposta = (id) => estado.respostas[id] || {};
const lista = (id) => (Array.isArray(resposta(id).valor) ? resposta(id).valor : []);

// ------------------------------------------------------------------ fluxo

function setoresSugeridos() {
  const pontos = {};
  lista('situacoes').forEach((situacao, ordem) => {
    (SITUACAO_PARA_SETORES[situacao] || []).forEach((setor, peso) => {
      pontos[setor] = (pontos[setor] || 0) + 10 - peso - ordem * 0.01;
    });
  });
  return Object.keys(pontos).sort((a, b) => pontos[b] - pontos[a]).slice(0, 3);
}

function setoresCandidatos() {
  const escolhidos = lista('setor');
  return escolhidos.includes('nao-sei') ? setoresSugeridos() : escolhidos;
}

function setorAnalisado() {
  const candidatos = setoresCandidatos();
  const prioridade = resposta('prioridade').valor;
  return candidatos.includes(prioridade) ? prioridade : candidatos[0];
}

function proximaDe(id) {
  const valor = resposta(id).valor;
  switch (id) {
    case 'segmento': return 'conhece-iot';
    case 'conhece-iot': return 'usa-iot';
    case 'usa-iot': return valor === 'sim' ? 'uso-iot' : 'porte';
    case 'uso-iot': return 'porte';
    case 'porte': return 'unidades';
    case 'unidades': return 'horario';
    case 'horario': return 'setor';
    case 'setor':
      if (lista('setor').includes('nao-sei')) return 'situacoes';
      return lista('setor').length > 1 ? 'prioridade' : 'funcionarios';
    case 'situacoes': return 'prioridade';
    case 'prioridade': return 'funcionarios';
    case 'funcionarios': return 'area';
    case 'area': return PERGUNTAS_POR_SETOR[setorAnalisado()][0];
    default: {
      const perguntas = PERGUNTAS_POR_SETOR[setorAnalisado()] || [];
      const i = perguntas.indexOf(id);
      return i >= 0 && i < perguntas.length - 1 ? perguntas[i + 1] : null;
    }
  }
}

// ------------------------------------------------------------------ validação

function outroValido(r, cfg, selecionado) {
  return !cfg || !selecionado || Boolean((r.outro || '').trim());
}

function respondida(id) {
  const p = PERGUNTAS[id];
  const r = resposta(id);
  switch (p.tipo) {
    case 'unica':
      return Boolean(r.valor) && outroValido(r, p.outro, r.valor === p.outro?.valor);
    case 'multipla':
      return lista(id).length > 0 && outroValido(r, p.outro, lista(id).includes(p.outro?.valor));
    case 'colunas':
      return p.colunas.every((col) => r[col.chave]
        && outroValido({ outro: r[`${col.chave}_outro`] }, col.outro, r[col.chave] === col.outro?.valor));
    case 'texto':
      return Boolean((r.valor || '').trim());
    case 'moeda':
      return Number(r.valor) > 0;
    case 'numero':
      return Number.isInteger(r.valor) && r.valor > 0 && r.valor <= p.maximo;
    default:
      return true;
  }
}

function atualizarNavegacao() {
  const id = atual();
  el.proxima.disabled = !respondida(id);
  const ultima = respondida(id) && proximaDe(id) === null;
  el.proxima.textContent = ultima ? 'Finalizar >' : 'Próxima >';
}

function responder(id, dados) {
  estado.respostas[id] = { ...resposta(id), ...dados };
  salvar();
  atualizarNavegacao();
}

// ------------------------------------------------------------------ desenho

function criar(tag, classe, texto) {
  const no = document.createElement(tag);
  if (classe) no.className = classe;
  if (texto !== undefined) no.textContent = texto;
  return no;
}

function botaoOpcao(rotulo, marcado, multipla) {
  const btn = criar('button', multipla ? 'opcao multipla' : 'opcao');
  btn.type = 'button';
  btn.setAttribute('role', multipla ? 'checkbox' : 'radio');
  btn.setAttribute('aria-checked', String(marcado));
  btn.append(criar('i'), document.createTextNode(rotulo));
  return btn;
}

function campoOutro(cfg, valor, aoDigitar) {
  const caixa = criar('div', 'outro-detalhe');
  const id = `outro-${Math.random().toString(36).slice(2, 8)}`;
  const label = criar('label', '', cfg.label);
  label.htmlFor = id;
  const limite = cfg.area ? LIMITE_TEXTO : LIMITE_OUTRO;
  const campo = criar(cfg.area ? 'textarea' : 'input');
  campo.id = id;
  campo.maxLength = limite;
  campo.value = valor || '';
  if (cfg.area) campo.rows = 4; else campo.type = 'text';
  const contador = criar('small', 'contador');
  const contar = () => { contador.textContent = `${campo.value.length}/${limite}`; };
  campo.addEventListener('input', () => { contar(); aoDigitar(campo.value); });
  contar();
  caixa.append(label, campo, contador);
  return caixa;
}

function grupoOpcoes(opcoes, { multipla, marcados, aoClicar, rotulo }) {
  const grupo = criar('div', 'opcoes');
  grupo.setAttribute('role', multipla ? 'group' : 'radiogroup');
  grupo.setAttribute('aria-label', rotulo);
  opcoes.forEach(([valor, texto]) => {
    const btn = botaoOpcao(texto, marcados.includes(valor), multipla);
    btn.addEventListener('click', () => aoClicar(valor));
    grupo.append(btn);
  });
  return grupo;
}

function desenharEscolha(id, p) {
  const multipla = p.tipo === 'multipla';
  const opcoes = p.outro ? [...p.opcoes, [p.outro.valor, p.outro.rotulo]] : p.opcoes;
  const marcados = multipla ? lista(id) : [resposta(id).valor].filter(Boolean);

  const aoClicar = (valor) => {
    let novo;
    if (!multipla) {
      novo = valor;
    } else if (marcados.includes(valor)) {
      novo = marcados.filter((v) => v !== valor);
    } else if (valor === p.exclusiva) {
      novo = [valor];
    } else {
      novo = [...marcados.filter((v) => v !== p.exclusiva), valor];
    }
    responder(id, { valor: novo });
    desenhar();
  };

  el.corpo.append(grupoOpcoes(opcoes, { multipla, marcados, aoClicar, rotulo: p.titulo }));

  if (p.outro && marcados.includes(p.outro.valor)) {
    el.corpo.append(campoOutro(p.outro, resposta(id).outro, (texto) => responder(id, { outro: texto })));
  }

  if (p.explicacao && p.explicacao.includes(resposta(id).valor)) {
    el.corpo.append(explicacaoIoT());
  }
}

function desenharColunas(id, p) {
  const r = resposta(id);
  const grade = criar('div', 'colunas');
  p.colunas.forEach((col) => {
    const coluna = criar('div', 'coluna');
    coluna.append(criar('h2', '', col.titulo));
    const opcoes = col.outro ? [...col.opcoes, [col.outro.valor, col.outro.rotulo]] : col.opcoes;
    coluna.append(grupoOpcoes(opcoes, {
      multipla: false,
      marcados: [r[col.chave]].filter(Boolean),
      rotulo: col.titulo,
      aoClicar: (valor) => { responder(id, { [col.chave]: valor }); desenhar(); },
    }));
    if (col.outro && r[col.chave] === col.outro.valor) {
      coluna.append(campoOutro(col.outro, r[`${col.chave}_outro`],
        (texto) => responder(id, { [`${col.chave}_outro`]: texto })));
    }
    grade.append(coluna);
  });
  el.corpo.append(grade);
}

function desenharTexto(id, p) {
  const caixa = criar('div', 'resposta-texto');
  const campo = criar('textarea');
  campo.rows = 5;
  campo.maxLength = LIMITE_TEXTO;
  campo.placeholder = p.placeholder || '';
  campo.value = resposta(id).valor || '';
  campo.setAttribute('aria-labelledby', 'titulo-pergunta');
  const contador = criar('small', 'contador');
  const contar = () => { contador.textContent = `${campo.value.length}/${LIMITE_TEXTO}`; };
  campo.addEventListener('input', () => { contar(); responder(id, { valor: campo.value }); });
  contar();
  caixa.append(campo, contador);
  el.corpo.append(caixa);
}

const formatoMoeda = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function desenharMoeda(id) {
  const caixa = criar('div', 'resposta-moeda');
  caixa.append(criar('span', 'prefixo', 'R$'));
  const campo = criar('input');
  campo.type = 'text';
  campo.inputMode = 'numeric';
  campo.placeholder = '0,00';
  campo.setAttribute('aria-labelledby', 'titulo-pergunta');
  const valor = Number(resposta(id).valor) || 0;
  campo.value = valor ? formatoMoeda.format(valor) : '';
  // só aceita dígitos: os dois últimos são os centavos
  campo.addEventListener('input', () => {
    const digitos = campo.value.replace(/\D/g, '').replace(/^0+/, '').slice(0, 12);
    const reais = digitos ? Number(digitos) / 100 : 0;
    campo.value = digitos ? formatoMoeda.format(reais) : '';
    responder(id, { valor: reais });
  });
  caixa.append(campo);
  el.corpo.append(caixa);
}

// Número inteiro com unidade ao lado (ex.: área em m²). Só aceita dígitos.
function desenharNumero(id, p) {
  const caixa = criar('div', 'resposta-moeda');
  const campo = criar('input');
  campo.type = 'text';
  campo.inputMode = 'numeric';
  campo.placeholder = '0';
  campo.setAttribute('aria-labelledby', 'titulo-pergunta');
  campo.value = resposta(id).valor ? String(resposta(id).valor) : '';
  campo.addEventListener('input', () => {
    const digitos = campo.value.replace(/\D/g, '').replace(/^0+/, '').slice(0, String(p.maximo).length);
    campo.value = digitos;
    responder(id, { valor: digitos ? Number(digitos) : 0 });
  });
  caixa.append(campo, criar('span', 'prefixo', p.unidade));
  el.corpo.append(caixa);
}

function explicacaoIoT() {
  const caixa = criar('aside', 'explicacao');
  caixa.append(
    criar('h2', '', 'O que é IoT?'),
    criar('p', '', 'IoT, ou Internet das Coisas, é uma tecnologia que conecta sensores e dispositivos à internet para coletar e transmitir informações sobre o funcionamento de ambientes, equipamentos e processos em tempo real.'),
    criar('p', '', 'Com esses dados, sua empresa consegue acompanhar o que acontece na operação, identificar problemas, evitar desperdícios e tomar decisões mais inteligentes.'),
    criar('h2', '', 'Como a Bzu Tech pode ajudar?'),
    criar('p', '', 'A Bzu Tech fornece e conecta sensores capazes de monitorar diferentes variáveis, como temperatura, umidade, qualidade do ar, ruído e condições elétricas.'),
    criar('p', '', 'Essas informações são transformadas em dados que ajudam sua empresa a acompanhar a operação, identificar oportunidades de melhoria e aumentar a eficiência.'),
  );
  const final = criar('p');
  final.append('Na prática, isso significa ', criar('strong', '', 'transformar dados em decisões melhores'), '.');
  caixa.append(final);
  return caixa;
}

function prepararPrioridade(p) {
  const candidatos = setoresCandidatos();
  p.opcoes = candidatos.map((setor) => [setor, SETORES[setor]]);
  const sugestao = lista('setor').includes('nao-sei');
  if (candidatos.length === 1) {
    p.titulo = `Vamos então analisar o setor “${SETORES[candidatos[0]]}” da sua operação.`;
    p.instrucao = 'Com base nas situações que você marcou, este é o setor em que a IoT pode ajudar primeiro. Confirme para continuar.';
  } else {
    p.titulo = 'Qual dessas operações você deseja analisar primeiro?';
    p.instrucao = sugestao
      ? 'Cruzando as situações que você marcou com os sensores da Bzu, estes são os setores com mais potencial.'
      : 'Você marcou mais de um setor. Escolha por onde começar.';
  }
  if (!candidatos.includes(resposta('prioridade').valor)) {
    estado.respostas.prioridade = { valor: candidatos.length === 1 ? candidatos[0] : '' };
  }
}

function desenhar() {
  const id = atual();
  const p = PERGUNTAS[id];
  if (id === 'prioridade') prepararPrioridade(p);

  el.bloco.textContent = BLOCOS[p.bloco];
  el.numero.textContent = `Pergunta ${p.numero}`;
  el.titulo.textContent = p.titulo;
  const instrucao = p.instrucao || (p.tipo === 'multipla' ? 'Selecione uma ou mais opções.' : '');
  el.instrucao.textContent = instrucao;
  el.instrucao.hidden = !instrucao;
  const progresso = Math.min(100, Math.round((estado.historico.length / TOTAL_ESTIMADO) * 100));
  el.barra.style.width = `${progresso}%`;

  el.corpo.replaceChildren();
  if (p.tipo === 'unica' || p.tipo === 'multipla') desenharEscolha(id, p);
  else if (p.tipo === 'colunas') desenharColunas(id, p);
  else if (p.tipo === 'texto') desenharTexto(id, p);
  else if (p.tipo === 'moeda') desenharMoeda(id);
  else if (p.tipo === 'numero') desenharNumero(id, p);

  atualizarNavegacao();
}

function irPara(id) {
  estado.historico.push(id);
  salvar();
  desenhar();
  el.titulo.focus({ preventScroll: true });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ------------------------------------------------------------------ fim

function respostasDoCaminho() {
  const saida = {};
  estado.historico.forEach((id) => { saida[id] = estado.respostas[id]; });
  return saida;
}

// Maturidade de coleta de dados, usada pelo chat (chat.js lê 'bzu_coleta').
const COLETA_POR_USO = {
  frequente: 'sensoriamento', 'ja-iot': 'sensoriamento', 'sem-central': 'sensoriamento',
  periodico: 'planilha-manual', manual: 'planilha-manual', 'nao-sei': 'planilha-manual',
  nenhum: 'nao-coletamos',
};

function mostrarErro(mensagem) {
  const caixa = document.getElementById('erro-envio');
  caixa.textContent = mensagem;
  caixa.hidden = !mensagem;
}

async function enviarRespostas(respostas, setor) {
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  const resp = await fetch(el.proxima.dataset.api, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
    body: JSON.stringify({ respostas, setor_analisado: setor }),
  });
  const dados = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(dados.erro || 'Não foi possível salvar suas respostas.');
  return dados;
}

async function finalizar() {
  el.proxima.disabled = true;
  el.proxima.textContent = 'Salvando...';
  mostrarErro('');
  let dados;
  try {
    // O servidor salva as respostas e cria a Simulacao (status "pendente").
    dados = await enviarRespostas(respostasDoCaminho(), setorAnalisado());
  } catch (erro) {
    mostrarErro(erro instanceof TypeError ? 'Sem conexão com o servidor. Tente novamente.' : erro.message);
    atualizarNavegacao();
    return;
  }

  try {
    const coleta = resposta('usa-iot').valor === 'sim'
      ? COLETA_POR_USO[resposta('uso-iot').valor] || 'planilha-manual'
      : 'nao-coletamos';
    sessionStorage.setItem('bzu_coleta', coleta);
    sessionStorage.removeItem(CHAVE_ESTADO); // questionário concluído: a próxima visita começa do zero
  } catch (_) {}

  // A página de resultado mostra o carregamento enquanto a simulação roda.
  window.location.assign(dados.url_resultado);
}

// ------------------------------------------------------------------ eventos

el.proxima.addEventListener('click', () => {
  const id = atual();
  if (!respondida(id)) return;
  const proxima = proximaDe(id);
  if (proxima) irPara(proxima); else finalizar();
});

el.anterior.addEventListener('click', () => {
  if (estado.historico.length <= 1) {
    window.location.assign(el.anterior.dataset.url);
    return;
  }
  estado.historico.pop();
  salvar();
  desenhar();
  el.titulo.focus({ preventScroll: true });
});

carregar();
desenhar();
