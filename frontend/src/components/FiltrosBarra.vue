<script setup>
defineProps({
  estados: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="filtros cartao">
    <label>
      Estado
      <select
        :value="modelValue.estado"
        @change="emit('update:modelValue', { ...modelValue, estado: $event.target.value })"
      >
        <option value="">Todos</option>
        <option v-for="estado in estados" :key="estado.id" :value="estado.sigla">
          {{ estado.nome }} ({{ estado.sigla }})
        </option>
      </select>
    </label>

    <label>
      Região
      <select
        :value="modelValue.regiao"
        @change="emit('update:modelValue', { ...modelValue, regiao: $event.target.value })"
        >
        <option value="">Todas</option>
        <option v-for="regiao in ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']" :key="regiao" :value="regiao">
          {{ regiao }}
        </option>
      </select>
    </label>

    <label>
      Buscar município
      <input
        type="text"
        placeholder="ex.: joao pessoa"
        :value="modelValue.nomeMunicipio"
        @input="emit('update:modelValue', { ...modelValue, nomeMunicipio: $event.target.value })"
      />
    </label>

    <label>
      Ordenar por
      <select
        :value="modelValue.ordenarPor"
        @change="emit('update:modelValue', { ...modelValue, ordenarPor: $event.target.value })"
      >
        <option value="populacao">População</option>
        <option value="renda_media">Renda média</option>
        <option value="renda_mediana">Renda mediana</option>
        <option value="indice_envelhecimento">Índice de envelhecimento</option>
      </select>
    </label>

    <label>
      Direção
      <select
        :value="modelValue.direcao"
        @change="emit('update:modelValue', { ...modelValue, direcao: $event.target.value })"
      >
        <option value="desc">Maior primeiro</option>
        <option value="asc">Menor primeiro</option>
      </select>
    </label>
  </div>
</template>

<style scoped>
.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}

.filtros label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 220px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--cor-texto-muted);
}

.filtros select,
.filtros input {
  font-family: inherit;
  font-size: 14px;
  font-weight: 400;
  text-transform: none;
  letter-spacing: normal;
  color: var(--cor-texto);
  background: #ffffff;
  border: 1px solid #d6d5cd;
  border-radius: 8px;
  padding: 10px 12px;
}

.filtros select:focus,
.filtros input:focus {
  outline: 2px solid var(--cor-accent);
  outline-offset: 1px;
}
</style>
