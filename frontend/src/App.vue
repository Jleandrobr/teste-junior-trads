<script setup>
import { ref, onMounted } from "vue";


const API_URL = "http://localhost:8000";

const estados = ref([]);
const carregando = ref(true);
const erro = ref(null);

async function buscarEstados() {
  try {
    const resposta = await fetch(`${API_URL}/api/v1/estados`);
    if (!resposta.ok) {
      throw new Error(`API respondeu ${resposta.status}`);
    }
    estados.value = await resposta.json();
  } catch (e) {
    erro.value = e.message;
  } finally {
    carregando.value = false;
  }
}

onMounted(buscarEstados);
</script>

<template>
  <main>
    <h1>Painel de Inteligência de Mercado</h1>

    <p v-if="carregando">Carregando estados...</p>
    <p v-else-if="erro">Erro ao falar com a API: {{ erro }}</p>
    <p v-else>Conectado à API - {{ estados.length }} estados carregados.</p>
  </main>
</template>
