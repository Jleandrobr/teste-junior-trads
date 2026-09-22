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
  <div class="filtros">
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
  margin-bottom: 24px;
}

.filtros label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  gap: 4px;
}
</style>
