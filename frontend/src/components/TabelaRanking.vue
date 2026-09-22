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
  <div class="cartao tabela-container">
    <h2>Ranking de municípios</h2>
    <table class="tabela-ranking">
      <thead>
        <tr>
          <th class="col-rank"></th>
          <th>Município</th>
          <th>Estado</th>
          <th class="col-numero">População</th>
          <th class="col-numero">Renda média</th>
          <th class="col-numero">Índice envelh.</th>
          <th class="col-numero">Nº empresas</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="municipios.length === 0">
          <td colspan="7">Nenhum município encontrado com esse filtro.</td>
        </tr>
        <tr v-for="(municipio, indice) in municipios" :key="municipio.id" :class="{ destaque: indice === 0 }">
          <td class="col-rank"><span class="selo-rank">{{ indice + 1 }}</span></td>
          <td>{{ municipio.nome }}</td>
          <td class="col-estado">{{ municipio.estado }}</td>
          <td class="col-numero">{{ formatarNumero(municipio.populacao) }}</td>
          <td class="col-numero">{{ formatarMoeda(municipio.renda_media) }}</td>
          <td class="col-numero">{{ municipio.indice_envelhecimento.toFixed(1) }}</td>
          <td class="col-numero">{{ formatarNumero(municipio.qtd_empresas) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.tabela-container {
  flex-grow: 1;
  min-width: 0;
}

.tabela-ranking {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.tabela-ranking th {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--cor-borda);
  color: var(--cor-texto-muted);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.tabela-ranking td {
  padding: 10px;
  border-bottom: 1px solid #efeee8;
}

.tabela-ranking tbody tr:nth-child(even) {
  background: #faf9f6;
}

.tabela-ranking tbody tr.destaque {
  background: var(--cor-accent-fundo);
}

.col-numero {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.col-estado {
  color: #4c5a55;
}

.col-rank {
  width: 28px;
}

.selo-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid var(--cor-borda);
  font-size: 11px;
  font-weight: 600;
  color: var(--cor-texto-muted);
}

.destaque .selo-rank {
  background: var(--cor-accent);
  border-color: var(--cor-accent);
  color: #ffffff;
}
</style>
