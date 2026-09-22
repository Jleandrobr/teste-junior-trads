<script setup>
import { ref, reactive, onMounted } from "vue";
import { buscarEstados, buscarMunicipios } from "./api.js";
import FiltrosBarra from "./components/FiltrosBarra.vue";
import TabelaRanking from "./components/TabelaRanking.vue";
import GraficoDispersao from "./components/GraficoDispersao.vue";

const estados = ref([]);
const municipios = ref([]);
const carregando = ref(true);
const erro = ref(null);

const filtros = reactive({
  estado: "",
  nomeMunicipio: "",
  ordenarPor: "populacao",
  direcao: "desc",
});

async function carregarMunicipios() {
  try {
    municipios.value = await buscarMunicipios({
      estado: filtros.estado,
      nomeMunicipio: filtros.nomeMunicipio,
      ordenarPor: filtros.ordenarPor,
      direcao: filtros.direcao,
      limite: 50,
    });
    erro.value = null;
  } catch (e) {
    erro.value = e.message;
  } finally {
    carregando.value = false;
  }
}

let temporizadorBusca = null;
function atualizarFiltros(novosFiltros) {
  Object.assign(filtros, novosFiltros);

  clearTimeout(temporizadorBusca);
  temporizadorBusca = setTimeout(carregarMunicipios, 900);
}

onMounted(async () => {
  try {
    estados.value = await buscarEstados();
  } catch (e) {
    erro.value = e.message;
  }
  await carregarMunicipios();
});
</script>

<template>
  <main>
    <h1>Painel de Inteligência de Mercado</h1>

    <FiltrosBarra :estados="estados" :model-value="filtros" @update:model-value="atualizarFiltros" />

    <p v-if="erro">Erro ao falar com a API: {{ erro }}</p>
    <p v-else-if="carregando">Carregando...</p>
    <template v-else>
      <GraficoDispersao :municipios="municipios" />
      <TabelaRanking :municipios="municipios" />
    </template>
  </main>
</template>

<style>
body {
  font-family: system-ui, sans-serif;
  margin: 0;
  padding: 24px;
}
</style>
