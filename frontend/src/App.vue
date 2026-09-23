<script setup>
import { ref, reactive, onMounted } from "vue";
import { buscarEstados, buscarMunicipios } from "./api.js";
import FiltrosBarra from "./components/FiltrosBarra.vue";
import TabelaRanking from "./components/TabelaRanking.vue";
import GraficoDispersao from "./components/GraficoDispersao.vue";

const LIMITE_POR_PAGINA = 50;

const estados = ref([]);
const municipios = ref([]);
const totalMunicipios = ref(0);
const paginaAtual = ref(1);
const carregando = ref(true);
const erro = ref(null);

const filtros = reactive({
  estado: "",
  nomeMunicipio: "",
  regiao: "",
  ordenarPor: "populacao",
  direcao: "desc",
});

async function carregarMunicipios() {
  try {
    const resposta = await buscarMunicipios({
      estado: filtros.estado,
      regiao: filtros.regiao,
      nomeMunicipio: filtros.nomeMunicipio,
      ordenarPor: filtros.ordenarPor,
      direcao: filtros.direcao,
      limite: LIMITE_POR_PAGINA,
      offset: (paginaAtual.value - 1) * LIMITE_POR_PAGINA,
    });
    municipios.value = resposta.resultados;
    totalMunicipios.value = resposta.total;
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
  paginaAtual.value = 1;

  clearTimeout(temporizadorBusca);
  temporizadorBusca = setTimeout(carregarMunicipios, 900);
}

function irParaPagina(novaPagina) {
  paginaAtual.value = novaPagina;
  carregarMunicipios();
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
    <header class="cabecalho">
      <div>
        <h1>Painel de Inteligência de Mercado</h1>
        <p class="subtitulo">Trads Corretora - 5.570 municípios · dados do IBGE</p>
      </div>
      <span class="selo">Dados de referência: 2021-2022</span>
    </header>

    <FiltrosBarra :estados="estados" :model-value="filtros" @update:model-value="atualizarFiltros" />

    <p v-if="erro" class="mensagem">Erro ao falar com a API: {{ erro }}</p>
    <p v-else-if="carregando" class="mensagem">Carregando...</p>
    <div v-else class="conteudo">
      <TabelaRanking
        :municipios="municipios"
        :offset="(paginaAtual - 1) * LIMITE_POR_PAGINA"
        :total="totalMunicipios"
        :pagina-atual="paginaAtual"
        :limite-por-pagina="LIMITE_POR_PAGINA"
        @mudar-pagina="irParaPagina"
      />
      <GraficoDispersao :municipios="municipios" />
    </div>
  </main>
</template>

<style>
:root {
  --cor-fundo: #f5f4f1;
  --cor-texto: #1c1f1e;
  --cor-texto-titulo: #17211e;
  --cor-texto-muted: #6b7570;
  --cor-borda: #e4e3dc;
  --cor-accent: #0e6b5c;
  --cor-accent-fundo: #e1f0eb;
  --cor-destaque: #c1652f;
}

body {
  margin: 0;
  font-family: "Public Sans", system-ui, sans-serif;
  background: var(--cor-fundo);
  color: var(--cor-texto);
}

main {
  max-width: 1360px;
  margin: 0 auto;
  padding: 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.cabecalho {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.cabecalho h1 {
  margin: 0 0 6px 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--cor-texto-titulo);
}

.subtitulo {
  margin: 0;
  font-size: 14px;
  color: var(--cor-texto-muted);
}

.selo {
  font-size: 12px;
  font-weight: 600;
  color: #4c5a55;
  background: #ffffff;
  border: 1px solid #dedad6;
  border-radius: 999px;
  padding: 8px 16px;
  white-space: nowrap;
}

.mensagem {
  font-size: 14px;
  color: var(--cor-texto-muted);
}

.conteudo {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.cartao {
  background: #ffffff;
  border: 1px solid var(--cor-borda);
  border-radius: 12px;
  padding: 24px;
}

.cartao h2 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--cor-texto-titulo);
}
</style>
