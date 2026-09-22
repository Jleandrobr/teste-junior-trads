<script setup>
defineProps({
  municipios: {
    type: Array,
    required: true,
  },
});

function formatarNumero(valor) {
  return new Intl.NumberFormat("pt-BR").format(valor);
}

function formatarMoeda(valor) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);
}
</script>

<template>
  <table class="tabela-ranking">
    <thead>
      <tr>
        <th>Município</th>
        <th>Estado</th>
        <th>População</th>
        <th>Renda média</th>
        <th>Índice de envelhecimento</th>
        <th>Nº empresas</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="municipios.length === 0">
        <td colspan="6">Nenhum município encontrado com esse filtro.</td>
      </tr>
      <tr v-for="municipio in municipios" :key="municipio.id">
        <td>{{ municipio.nome }}</td>
        <td>{{ municipio.estado }}</td>
        <td>{{ formatarNumero(municipio.populacao) }}</td>
        <td>{{ formatarMoeda(municipio.renda_media) }}</td>
        <td>{{ municipio.indice_envelhecimento.toFixed(1) }}</td>
        <td>{{ formatarNumero(municipio.qtd_empresas) }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.tabela-ranking {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 32px;
}

.tabela-ranking th,
.tabela-ranking td {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
}

.tabela-ranking th {
  font-weight: 600;
  background: #f5f5f5;
}
</style>
