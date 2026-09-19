from pydantic import BaseModel, ConfigDict, Field


class RegiaoIBGE(BaseModel):
    id: int
    sigla: str
    nome: str


class EstadoIBGE(BaseModel):
    id: int
    sigla: str
    nome: str
    regiao: RegiaoIBGE


class UFIBGE(BaseModel):
    id: int


class MesorregiaoIBGE(BaseModel):
    UF: UFIBGE


class MicrorregiaoIBGE(BaseModel):
    mesorregiao: MesorregiaoIBGE


class RegiaoIntermediariaIBGE(BaseModel):
    UF: UFIBGE


class RegiaoImediataIBGE(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    regiao_intermediaria: RegiaoIntermediariaIBGE = Field(alias="regiao-intermediaria")


class MunicipioIBGE(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    nome: str
    microrregiao: MicrorregiaoIBGE | None = None
    regiao_imediata: RegiaoImediataIBGE | None = Field(default=None, alias="regiao-imediata")

    @property
    def estado_id(self) -> int:
        if self.microrregiao is not None:
            return self.microrregiao.mesorregiao.UF.id
        if self.regiao_imediata is not None:
            return self.regiao_imediata.regiao_intermediaria.UF.id
        raise ValueError(f"Município {self.id} sem microrregiao e sem regiao-imediata")
