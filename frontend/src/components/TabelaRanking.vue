<script setup>
import { computed } from "vue";
import { formatarNumero, formatarMoeda, formatarPercentual, formatarDecimal } from "../formatadores.js";

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
  visao: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["mudar-pagina", "mudar-visao"]);

const VISOES = [
  { id: "geral", rotulo: "Visão geral" },
  { id: "saude", rotulo: "Plano médico" },
  { id: "odonto", rotulo: "Plano odontológico" },
  { id: "empresarial", rotulo: "Empresarial" },
];

const COLUNAS_POR_VISAO = {
  geral: [
    { campo: "populacao", rotulo: "População", formato: formatarNumero },
    {
      campo: "renda_per_capita_mediana",
      rotulo: "Renda per capita mediana",
      formato: formatarMoeda,
      dica: "Renda domiciliar dividida pelos moradores, mediana do município (Censo 2022). Metade da população vive com menos que isso",
    },
    {
      campo: "renda_per_capita_media",
      rotulo: "Renda per capita média",
      formato: formatarMoeda,
      dica: "Renda domiciliar dividida pelos moradores, média do município (Censo 2022)",
    },
    { campo: "idade_mediana", rotulo: "Idade mediana", formato: formatarDecimal },
    { campo: "indice_envelhecimento", rotulo: "Índice envelh.", formato: formatarDecimal },
  ],
  saude: [
    { campo: "populacao", rotulo: "População", formato: formatarNumero },
    { campo: "qtd_beneficiarios_medicos", rotulo: "Beneficiários", formato: formatarNumero },
    {
      campo: "percentual_adesao_plano_medico",
      rotulo: "% de adesão",
      formato: formatarPercentual,
      barra: true,
      dica: "Beneficiários de plano médico-hospitalar (ANS 2026) divididos pela população (IBGE 2021)",
    },
    {
      campo: "populacao_sem_plano_medico",
      rotulo: "Sem plano médico",
      formato: formatarNumero,
      dica: "População (IBGE 2021) menos beneficiários de plano médico-hospitalar (ANS 2026)",
    },
    { campo: "renda_per_capita_media", rotulo: "Renda per capita média", formato: formatarMoeda },
  ],
  odonto: [
    { campo: "populacao", rotulo: "População", formato: formatarNumero },
    {
      campo: "qtd_beneficiarios_odonto",
      rotulo: "Beneficiários",
      formato: formatarNumero,
      dica: "Beneficiários de planos exclusivamente odontológicos (ANS 2026)",
    },
    { campo: "percentual_adesao_odonto", rotulo: "% de adesão", formato: formatarPercentual, barra: true },
    { campo: "populacao_sem_odonto", rotulo: "Sem plano odonto", formato: formatarNumero },
    { campo: "renda_per_capita_media", rotulo: "Renda per capita média", formato: formatarMoeda },
  ],
  empresarial: [
    { campo: "qtd_empresas", rotulo: "Empresas", formato: formatarNumero },
    { campo: "empresas_por_mil_habitantes", rotulo: "Empresas / mil hab.", formato: formatarDecimal },
    { campo: "pessoal_assalariado", rotulo: "Assalariados", formato: formatarNumero },
    { campo: "assalariados_por_mil_habitantes", rotulo: "Assalariados / mil hab.", formato: formatarDecimal },
  ],
};

const colunas = computed(() => COLUNAS_POR_VISAO[props.visao]);
const totalPaginas = computed(() => Math.max(1, Math.ceil(props.total / props.limitePorPagina)));
</script>

<template>
  <div class="cartao tabela-container">
    <div class="tabela-cabecalho">
      <h2>Ranking de municípios</h2>
      <div class="abas" role="tablist">
        <button
          v-for="opcao in VISOES"
          :key="opcao.id"
          role="tab"
          :aria-selected="opcao.id === visao"
          :class="{ ativa: opcao.id === visao }"
          @click="emit('mudar-visao', opcao.id)"
        >
          {{ opcao.rotulo }}
        </button>
      </div>
    </div>

    <div class="tabela-scroll">
    <table class="tabela-ranking">
      <thead>
        <tr>
          <th class="col-rank"></th>
          <th>Município</th>
          <th>UF</th>
          <th v-for="coluna in colunas" :key="coluna.campo" class="col-numero" :title="coluna.dica">
            {{ coluna.rotulo }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="municipios.length === 0">
          <td :colspan="colunas.length + 3">Nenhum município encontrado com esse filtro.</td>
        </tr>
        <tr
          v-for="(municipio, indice) in municipios"
          :key="municipio.id"
          :class="{ destaque: offset + indice === 0 }"
        >
          <td class="col-rank"><span class="selo-rank">{{ offset + indice + 1 }}</span></td>
          <td>{{ municipio.nome }}</td>
          <td class="col-estado">{{ municipio.estado }}</td>
          <td v-for="coluna in colunas" :key="coluna.campo" class="col-numero">
            {{ coluna.formato(municipio[coluna.campo]) }}
            <span v-if="coluna.barra" class="barra">
              <span class="barra-preenchida" :style="{ width: Math.min(100, municipio[coluna.campo]) + '%' }"></span>
            </span>
          </td>
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

.tabela-ranking .col-numero {
  text-align: center;
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

.tabela-cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.tabela-cabecalho h2 {
  margin: 0;
}

.abas {
  display: flex;
  gap: 4px;
  background: #f5f4f1;
  border: 1px solid var(--cor-borda);
  border-radius: 10px;
  padding: 3px;
}

.abas button {
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--cor-texto-muted);
  background: transparent;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
}

.abas button.ativa {
  color: #ffffff;
  background: var(--cor-accent);
}

.barra {
  display: block;
  height: 4px;
  margin-top: 4px;
  background: #efeee8;
  border-radius: 999px;
  overflow: hidden;
}

.barra-preenchida {
  display: block;
  height: 100%;
  background: var(--cor-accent);
}

@media (max-width: 768px) {
  .abas {
    max-width: 100%;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .abas button {
    white-space: nowrap;
  }

  .paginacao {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
