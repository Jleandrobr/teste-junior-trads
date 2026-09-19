from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Estado(Base):
    __tablename__ = "estados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    sigla: Mapped[str] = mapped_column(String(2), unique=True)
    nome: Mapped[str] = mapped_column(String(100))
    regiao: Mapped[str] = mapped_column(String(50))

    municipios: Mapped[list["Municipio"]] = relationship(back_populates="estado")


class Municipio(Base):
    __tablename__ = "municipios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    nome: Mapped[str] = mapped_column(String(100))
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"))

    estado: Mapped["Estado"] = relationship(back_populates="municipios")


class Populacao(Base):
    __tablename__ = "populacao"
    __table_args__ = (UniqueConstraint("municipio_id", "ano"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    ano: Mapped[int]
    populacao: Mapped[int]


class PerfilDemografico(Base):
    __tablename__ = "perfil_demografico"
    __table_args__ = (UniqueConstraint("municipio_id", "ano"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    ano: Mapped[int]
    indice_envelhecimento: Mapped[float] = mapped_column(Numeric(10, 2))
    idade_mediana: Mapped[float] = mapped_column(Numeric(5, 2))
    razao_sexo: Mapped[float] = mapped_column(Numeric(10, 2))


class Renda(Base):
    __tablename__ = "renda"
    __table_args__ = (UniqueConstraint("municipio_id", "ano"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    ano: Mapped[int]
    rendimento_medio: Mapped[float] = mapped_column(Numeric(10, 2))
    rendimento_mediano: Mapped[float] = mapped_column(Numeric(10, 2))


class Empresa(Base):
    __tablename__ = "empresas"
    __table_args__ = (UniqueConstraint("municipio_id", "ano"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    ano: Mapped[int]
    qtd_empresas: Mapped[int]
    pessoal_assalariado: Mapped[int]
    salarios_mil_reais: Mapped[float] = mapped_column(Numeric(14, 2))
