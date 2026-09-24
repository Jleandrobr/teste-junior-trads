<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { Chart } from "chart.js/auto";

const props = defineProps({
  municipios: {
    type: Array,
    required: true,
  },
});

const canvasRef = ref(null);
let grafico = null;

const modoEixoY = ref("envelhecimento");

const tituloDoGrafico = computed(() =>
  modoEixoY.value === "adesao" ? "Renda × % de adesão" : "Renda × envelhecimento"
);

const legendaDoGrafico = computed(() =>
  modoEixoY.value === "adesao"
    ? "Tamanho da bolha = população sem plano médico. Alvo: renda alta e adesão baixa (canto inferior direito)"
    : "Tamanho da bolha = população"
);

const CINZA_GRADE = "#e4e3dc";
const CINZA_TEXTO = "#6b7570";

function raioDaBolha(tamanho) {
  return Math.min(28, Math.max(4, Math.sqrt(tamanho) / 50));
}

function formatarPercentual(valor) {
  const numero = valor.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  return `${numero}%`;
}

function montarPontos(municipios) {
  return municipios.map((municipio) => {
    if (modoEixoY.value === "adesao") {
      return {
        x: municipio.renda_media,
        y: municipio.percentual_adesao_plano_medico,
        r: raioDaBolha(municipio.populacao_sem_plano_medico),
        nome: municipio.nome,
        populacao: municipio.populacao,
        semPlano: municipio.populacao_sem_plano_medico,
      };
    }

    return {
      x: municipio.renda_media,
      y: municipio.indice_envelhecimento,
      r: raioDaBolha(municipio.populacao),
      nome: municipio.nome,
      populacao: municipio.populacao,
    };
  });
}

function desenharGrafico() {
  if (grafico) {
    grafico.destroy();
  }

  const modoAdesao = modoEixoY.value === "adesao";

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
                `Renda média: ${ponto.x.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}`,
              ];

              if (modoAdesao) {
                linhas.push(`% de adesão: ${formatarPercentual(ponto.y)}`);
                linhas.push(`Sem plano médico: ${ponto.semPlano.toLocaleString("pt-BR")}`);
              } else {
                linhas.push(`Índice de envelhecimento: ${ponto.y.toFixed(1)}`);
              }

              linhas.push(`População: ${ponto.populacao.toLocaleString("pt-BR")}`);
              return linhas;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Renda média (R$)", color: CINZA_TEXTO },
          grid: { color: CINZA_GRADE },
          ticks: { color: CINZA_TEXTO },
        },
        y: {
          title: {
            display: true,
            text: modoAdesao ? "% de adesão a plano médico" : "Índice de envelhecimento",
            color: CINZA_TEXTO,
          },
          beginAtZero: modoAdesao,
          grid: { color: CINZA_GRADE },
          ticks: {
            color: CINZA_TEXTO,
            callback: (valor) => (modoAdesao ? `${valor}%` : valor),
          },
        },
      },
    },
  });
}

onMounted(desenharGrafico);
watch(() => props.municipios, desenharGrafico);
watch(modoEixoY, desenharGrafico);
</script>

<template>
  <div class="cartao grafico-container">
    <div class="grafico-cabecalho">
      <h2>{{ tituloDoGrafico }}</h2>
      <select v-model="modoEixoY" aria-label="Eixo vertical do gráfico">
        <option value="envelhecimento">Envelhecimento</option>
        <option value="adesao">% de adesão</option>
      </select>
    </div>
    <p class="legenda">{{ legendaDoGrafico }}</p>
    <div class="grafico-canvas">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
.grafico-container {
  width: 480px;
  flex-shrink: 0;
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
