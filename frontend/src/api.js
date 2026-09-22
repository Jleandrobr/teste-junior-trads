const API_URL = "http://localhost:8000";

export async function buscarEstados() {
  const resposta = await fetch(`${API_URL}/api/v1/estados`);
  if (!resposta.ok) {
    throw new Error(`API respondeu ${resposta.status} ao buscar estados`);
  }
  return resposta.json();
}

export async function buscarMunicipios({ estado, nomeMunicipio, ordenarPor, direcao, limite }) {
  const params = new URLSearchParams();
  if (estado) params.set("estado", estado);
  if (nomeMunicipio) params.set("nome_municipio", nomeMunicipio);
  if (ordenarPor) params.set("ordenar_por", ordenarPor);
  if (direcao) params.set("direcao", direcao);
  if (limite) params.set("limite", limite);

  const resposta = await fetch(`${API_URL}/api/v1/municipios?${params.toString()}`);
  if (!resposta.ok) {
    throw new Error(`API respondeu ${resposta.status} ao buscar municípios`);
  }
  return resposta.json();
}
