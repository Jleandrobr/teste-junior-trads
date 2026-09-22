<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart } from "chart.js/auto";

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

function raioDaBolha(populacao) {
  return Math.min(28, Math.max(4, Math.sqrt(populacao) / 50));
}

function montarPontos(municipios) {
  return municipios.map((municipio) => ({
    x: municipio.renda_media,
    y: municipio.indice_envelhecimento,
    r: raioDaBolha(municipio.populacao),
    nome: municipio.nome,
    populacao: municipio.populacao,
  }));
}

function desenharGrafico() {
  if (grafico) {
    grafico.destroy();
  }

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
              return [
                ponto.nome,
                `Renda média: ${ponto.x.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}`,
                `Índice de envelhecimento: ${ponto.y.toFixed(1)}`,
                `População: ${ponto.populacao.toLocaleString("pt-BR")}`,
              ];
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
          title: { display: true, text: "Índice de envelhecimento", color: CINZA_TEXTO },
          grid: { color: CINZA_GRADE },
          ticks: { color: CINZA_TEXTO },
        },
      },
    },
  });
}

onMounted(desenharGrafico);
watch(() => props.municipios, desenharGrafico);
</script>

<template>
  <div class="cartao grafico-container">
    <h2>Renda × envelhecimento</h2>
    <p class="legenda">Tamanho da bolha = população</p>
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
