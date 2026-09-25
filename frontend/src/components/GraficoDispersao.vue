<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { Chart } from "chart.js/auto";
import { formatarNumero, formatarMoeda, formatarPercentual, formatarDecimal } from "../formatadores.js";

const props = defineProps({
  municipios: {
    type: Array,
    required: true,
  },
});

const canvasRef = ref(null);
let grafico = null;

const CINZA_GRADE = "#e4e3dc";
const CINZA_TEXTO = "#6b7570";

const MODOS = {
  envelhecimento: {
    rotulo: "Envelhecimento",
    titulo: "Renda per capita × envelhecimento",
    legenda: "Tamanho da bolha = população",
    eixoY: "Índice de envelhecimento",
    campoY: "indice_envelhecimento",
    campoBolha: "populacao",
    formatarY: (valor) => formatarDecimal(valor),
    linhaY: "Índice de envelhecimento",
    linhaBolha: null,
  },
  adesao: {
    rotulo: "% de adesão (médico)",
    titulo: "Renda per capita × % de adesão ao plano médico",
    legenda:
      "Tamanho da bolha = população sem plano médico. Alvo: renda alta e adesão baixa (canto inferior direito)",
    eixoY: "% de adesão a plano médico",
    campoY: "percentual_adesao_plano_medico",
    campoBolha: "populacao_sem_plano_medico",
    formatarY: formatarPercentual,
    linhaY: "% de adesão",
    linhaBolha: "Sem plano médico",
    comecaEmZero: true,
  },
  adesao_odonto: {
    rotulo: "% de adesão (odonto)",
    titulo: "Renda per capita × % de adesão ao plano odontológico",
    legenda:
      "Tamanho da bolha = população sem plano odontológico. Alvo: renda alta e adesão baixa (canto inferior direito)",
    eixoY: "% de adesão a plano odontológico",
    campoY: "percentual_adesao_odonto",
    campoBolha: "populacao_sem_odonto",
    formatarY: formatarPercentual,
    linhaY: "% de adesão odonto",
    linhaBolha: "Sem plano odontológico",
    comecaEmZero: true,
  },
  empresas: {
    rotulo: "Empresas por mil hab.",
    titulo: "Renda per capita × densidade empresarial",
    legenda:
      "Tamanho da bolha = número de empresas. Alvo: renda alta e muitas empresas por habitante (canto superior direito)",
    eixoY: "Empresas por mil habitantes",
    campoY: "empresas_por_mil_habitantes",
    campoBolha: "qtd_empresas",
    formatarY: formatarDecimal,
    linhaY: "Empresas por mil hab.",
    linhaBolha: "Empresas",
    comecaEmZero: true,
  },
};

const modo = ref("adesao");
const configuracao = computed(() => MODOS[modo.value]);

function raioDaBolha(tamanho) {
  return Math.min(28, Math.max(4, Math.sqrt(tamanho) / 50));
}

function montarPontos(municipios) {
  const { campoY, campoBolha } = configuracao.value;
  return municipios.map((municipio) => ({
    x: municipio.renda_per_capita_media,
    y: municipio[campoY],
    r: raioDaBolha(municipio[campoBolha]),
    nome: municipio.nome,
    populacao: municipio.populacao,
    tamanho: municipio[campoBolha],
  }));
}

function desenharGrafico() {
  if (grafico) {
    grafico.destroy();
  }

  const config = configuracao.value;

  grafico = new Chart(canvasRef.value, {
    type: "bubble",
    data: {
      datasets: [
        {
          label: "Municípios",
          data: montarPontos(props.municipios),
          backgroundColor: "rgba(14, 107, 92, 0.35)",
          borderColor: "rgba(14, 107, 92, 0.85)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      font: {
        family: "'Public Sans', system-ui, sans-serif",
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "#17211e",
          padding: 10,
          callbacks: {
            label(contexto) {
              const ponto = contexto.raw;
              const linhas = [
                ponto.nome,
                `Renda per capita média: ${formatarMoeda(ponto.x)}`,
                `${config.linhaY}: ${config.formatarY(ponto.y)}`,
              ];

              if (config.linhaBolha) {
                linhas.push(`${config.linhaBolha}: ${formatarNumero(ponto.tamanho)}`);
              }

              linhas.push(`População: ${formatarNumero(ponto.populacao)}`);
              return linhas;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Renda domiciliar per capita média (R$)", color: CINZA_TEXTO },
          grid: { color: CINZA_GRADE },
          ticks: { color: CINZA_TEXTO },
        },
        y: {
          title: { display: true, text: config.eixoY, color: CINZA_TEXTO },
          beginAtZero: Boolean(config.comecaEmZero),
          grid: { color: CINZA_GRADE },
          ticks: {
            color: CINZA_TEXTO,
            callback: (valor) => config.formatarY(valor),
          },
        },
      },
    },
  });
}

onMounted(desenharGrafico);
watch(() => props.municipios, desenharGrafico);
watch(modo, desenharGrafico);
</script>

<template>
  <div class="cartao grafico-container">
    <div class="grafico-cabecalho">
      <h2>{{ configuracao.titulo }}</h2>
      <select v-model="modo" aria-label="Eixo vertical do gráfico">
        <option v-for="(opcao, id) in MODOS" :key="id" :value="id">{{ opcao.rotulo }}</option>
      </select>
    </div>
    <p class="legenda">{{ configuracao.legenda }}</p>
    <div class="grafico-canvas">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
.grafico-container {
  flex: 1 1 100%;
  min-width: 0;
}

.grafico-cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.grafico-cabecalho h2 {
  margin: 0;
}

.grafico-cabecalho select {
  font-family: inherit;
  font-size: 12px;
  color: var(--cor-texto);
  background: #ffffff;
  border: 1px solid #d6d5cd;
  border-radius: 8px;
  padding: 6px 8px;
}

.legenda {
  margin: -10px 0 16px 0;
  font-size: 12px;
  color: var(--cor-texto-muted);
}

.grafico-canvas {
  position: relative;
  width: 100%;
  height: 380px;
}
</style>
