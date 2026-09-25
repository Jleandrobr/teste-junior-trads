<script setup>
import { computed } from "vue";
import { formatarNumero, formatarMoeda, formatarDecimal } from "../formatadores.js";

const props = defineProps({
  destaques: {
    type: Object,
    required: true,
  },
});

const cartoes = computed(() => {
  const d = props.destaques;
  return [
    {
      titulo: "Maior mercado sem plano médico",
      item: d.maior_mercado_sem_plano_medico,
      formatar: (valor) => `${formatarNumero(valor)} pessoas sem plano`,
    },
    {
      titulo: "Maior mercado sem odonto",
      item: d.maior_mercado_sem_odonto,
      formatar: (valor) => `${formatarNumero(valor)} pessoas sem plano`,
    },
    {
      titulo: "Maior densidade empresarial",
      item: d.maior_densidade_empresarial,
      formatar: (valor) => `${formatarDecimal(valor)} empresas por mil hab.`,
    },
    {
      titulo: "Maior renda per capita",
      item: d.maior_renda_per_capita,
      formatar: (valor) => formatarMoeda(valor),
    },
  ].filter((cartao) => cartao.item);
});
</script>

<template>
  <div v-if="cartoes.length > 0" class="destaques">
    <div v-for="cartao in cartoes" :key="cartao.titulo" class="cartao destaque-mercado">
      <span class="titulo">{{ cartao.titulo }}</span>
      <strong class="nome">{{ cartao.item.nome }} <small>{{ cartao.item.estado }}</small></strong>
      <span class="valor">{{ cartao.formatar(cartao.item.valor) }}</span>
    </div>
  </div>
</template>

<style scoped>
.destaques {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.destaque-mercado {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 18px 20px;
  border-left: 4px solid var(--cor-accent);
}

.titulo {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--cor-texto-muted);
}

.nome {
  font-size: 18px;
  color: var(--cor-texto-titulo);
}

.nome small {
  font-size: 12px;
  font-weight: 600;
  color: var(--cor-texto-muted);
}

.valor {
  font-size: 13px;
  color: var(--cor-accent);
  font-weight: 600;
}
</style>
