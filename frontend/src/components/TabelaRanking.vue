<script setup>
import { computed } from "vue";

const props = defineProps({
  municipios: {
    type: Array,
    required: true,
  },
  offset: {
    type: Number,
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
  paginaAtual: {
    type: Number,
    required: true,
  },
  limitePorPagina: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["mudar-pagina"]);

const totalPaginas = computed(() => Math.max(1, Math.ceil(props.total / props.limitePorPagina)));

function formatarNumero(valor) {
  return new Intl.NumberFormat("pt-BR").format(valor);
}

function formatarMoeda(valor) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);
}

function formatarPercentual(valor) {
  const numero = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(valor);
  return `${numero}%`;
}
</script>

<template>
  <div class="cartao tabela-container">
    <h2>Ranking de municípios</h2>
    <div class="tabela-scroll">
    <table class="tabela-ranking">
      <thead>
        <tr>
          <th class="col-rank"></th>
          <th>Município</th>
          <th>Estado</th>
          <th class="col-numero">População</th>
          <th
            class="col-numero"
            title="População (IBGE 2021) menos beneficiários de plano médico-hospitalar (ANS 2026)"
          >
            Sem plano médico
          </th>
          <th
            class="col-numero"
            title="Percentual da população com plano médico-hospitalar: beneficiários (ANS 2026) divididos pela população (IBGE 2021)"
          >
            % de adesão
          </th>
          <th class="col-numero">Renda média</th>
          <th class="col-numero">Índice envelh.</th>
          <th class="col-numero">Nº empresas</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="municipios.length === 0">
          <td colspan="9">Nenhum município encontrado com esse filtro.</td>
        </tr>
        <tr
          v-for="(municipio, indice) in municipios"
          :key="municipio.id"
          :class="{ destaque: offset + indice === 0 }"
        >
          <td class="col-rank"><span class="selo-rank">{{ offset + indice + 1 }}</span></td>
          <td>{{ municipio.nome }}</td>
          <td class="col-estado">{{ municipio.estado }}</td>
          <td class="col-numero">{{ formatarNumero(municipio.populacao) }}</td>
          <td class="col-numero">{{ formatarNumero(municipio.populacao_sem_plano_medico) }}</td>
          <td class="col-numero">{{ formatarPercentual(municipio.percentual_adesao_plano_medico) }}</td>
          <td class="col-numero">{{ formatarMoeda(municipio.renda_media) }}</td>
          <td class="col-numero">{{ municipio.indice_envelhecimento.toFixed(1) }}</td>
          <td class="col-numero">{{ formatarNumero(municipio.qtd_empresas) }}</td>
        </tr>
      </tbody>
    </table>
    </div>

    <div class="paginacao" v-if="total > 0">
      <span class="paginacao-info">
        Mostrando {{ offset + 1 }}-{{ Math.min(offset + municipios.length, total) }} de {{ formatarNumero(total) }}
      </span>
      <div class="paginacao-botoes">
        <button :disabled="paginaAtual === 1" @click="emit('mudar-pagina', paginaAtual - 1)">Anterior</button>
        <span>Página {{ paginaAtual }} de {{ totalPaginas }}</span>
        <button :disabled="paginaAtual === totalPaginas" @click="emit('mudar-pagina', paginaAtual + 1)">Próxima</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tabela-container {
  flex-grow: 1;
  min-width: 0;
}

.tabela-scroll {
  overflow-x: auto;
}

.tabela-ranking {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.tabela-ranking th {
  text-align: left;
  padding: 8px 6px;
  border-bottom: 1px solid var(--cor-borda);
  color: var(--cor-texto-muted);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.tabela-ranking td {
  padding: 10px 6px;
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

.paginacao {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 12px;
  color: var(--cor-texto-muted);
}

.paginacao-botoes {
  display: flex;
  align-items: center;
  gap: 10px;
}

.paginacao-botoes button {
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--cor-texto);
  background: #ffffff;
  border: 1px solid #d6d5cd;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
}

.paginacao-botoes button:disabled {
  color: var(--cor-texto-muted);
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
