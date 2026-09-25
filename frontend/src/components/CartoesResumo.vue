<script setup>
import { computed } from "vue";
import { formatarNumero, formatarMoeda, formatarPercentual, formatarCompacto } from "../formatadores.js";

const props = defineProps({
  resumo: {
    type: Object,
    required: true,
  },
});

const cartoes = computed(() => {
  const r = props.resumo;
  return [
    {
      titulo: "Municípios analisados",
      valor: formatarNumero(r.total_municipios),
      detalhe: `${formatarCompacto(r.populacao_total)} habitantes`,
    },
    {
      titulo: "Sem plano médico",
      valor: formatarCompacto(r.populacao_sem_plano_medico),
      detalhe: `Adesão de ${formatarPercentual(r.percentual_adesao_plano_medico)} · ${formatarCompacto(r.qtd_beneficiarios_medicos)} beneficiários`,
      destaque: true,
    },
    {
      titulo: "Sem plano odontológico",
      valor: formatarCompacto(r.populacao_sem_odonto),
      detalhe: `Adesão de ${formatarPercentual(r.percentual_adesao_odonto)} · ${formatarCompacto(r.qtd_beneficiarios_odonto)} beneficiários`,
      destaque: true,
    },
    {
      titulo: "Empresas",
      valor: formatarNumero(r.qtd_empresas),
      detalhe: `${formatarNumero(r.pessoal_assalariado)} assalariados`,
    },
    {
      titulo: "Renda per capita média",
      valor: formatarMoeda(r.renda_per_capita_media_ponderada),
      detalhe: "Renda domiciliar por morador, ponderada pela população",
    },
  ];
});
</script>

<template>
  <div class="cartoes-resumo">
    <div v-for="cartao in cartoes" :key="cartao.titulo" class="cartao cartao-resumo" :class="{ destaque: cartao.destaque }">
      <span class="titulo">{{ cartao.titulo }}</span>
      <strong class="valor">{{ cartao.valor }}</strong>
      <span class="detalhe">{{ cartao.detalhe }}</span>
    </div>
  </div>
</template>

<style scoped>
.cartoes-resumo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 16px;
}

.cartao-resumo {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
}

.titulo {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--cor-texto-muted);
}

.valor {
  font-family: "Space Grotesk", sans-serif;
  font-size: 28px;
  letter-spacing: -0.01em;
  color: var(--cor-texto-titulo);
}

.detalhe {
  font-size: 12px;
  color: var(--cor-texto-muted);
}

.cartao-resumo.destaque {
  border-color: var(--cor-accent);
  background: var(--cor-accent-fundo);
}

.cartao-resumo.destaque .valor {
  color: var(--cor-accent);
}

@media (max-width: 768px) {
  .cartoes-resumo {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .cartao-resumo {
    padding: 14px;
  }

  .valor {
    font-size: 22px;
  }
}
</style>
