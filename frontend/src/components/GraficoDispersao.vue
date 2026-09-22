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

function raioDaBolha(populacao) {
  return Math.max(4, Math.sqrt(populacao) / 50);
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
          backgroundColor: "rgba(37, 99, 235, 0.5)",
          borderColor: "rgba(37, 99, 235, 0.9)",
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
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
          title: { display: true, text: "Renda média (R$)" },
        },
        y: {
          title: { display: true, text: "Índice de envelhecimento" },
        },
      },
    },
  });
}

onMounted(desenharGrafico);
watch(() => props.municipios, desenharGrafico);
</script>

<template>
  <div class="grafico-container">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
.grafico-container {
  max-width: 800px;
  height: 500px;
  margin-bottom: 32px;
}
</style>
