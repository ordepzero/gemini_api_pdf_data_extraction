from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.connection import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(255), index=True)
    documento: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    criadoEm: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orcamentos: Mapped[list["Orcamento"]] = relationship(back_populates="cliente")


class Vendedor(Base):
    __tablename__ = "vendedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(255), index=True)
    telefone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    empresa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criadoEm: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orcamentos: Mapped[list["Orcamento"]] = relationship(back_populates="vendedor")


class Orcamento(Base):
    __tablename__ = "orcamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numeroOrcamento: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    dataEmissao: Mapped[str | None] = mapped_column(String(64), nullable=True)
    validade: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subtotal: Mapped[float | None] = mapped_column(Float, nullable=True)
    desconto: Mapped[float | None] = mapped_column(Float, nullable=True)
    frete: Mapped[float | None] = mapped_column(Float, nullable=True)
    impostos: Mapped[float | None] = mapped_column(Float, nullable=True)
    valorTotal: Mapped[float | None] = mapped_column(Float, nullable=True)
    observacoesGerais: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="Processado", index=True)
    arquivoOriginalNome: Mapped[str] = mapped_column(String(255))
    arquivoSalvoNome: Mapped[str] = mapped_column(String(255), unique=True)
    arquivoCaminho: Mapped[str] = mapped_column(String(1024), unique=True)
    criadoEm: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    clienteId: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    vendedorId: Mapped[int | None] = mapped_column(ForeignKey("vendedores.id"), nullable=True)

    cliente: Mapped[Cliente | None] = relationship(back_populates="orcamentos")
    vendedor: Mapped[Vendedor | None] = relationship(back_populates="orcamentos")
    itens: Mapped[list["ItemOrcamento"]] = relationship(
        back_populates="orcamento",
        cascade="all, delete-orphan",
    )


class ItemOrcamento(Base):
    __tablename__ = "itens_orcamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    orcamentoId: Mapped[int] = mapped_column(ForeignKey("orcamentos.id"), index=True)
    codigo: Mapped[str | None] = mapped_column(String(128), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    descricaoNormalizada: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantidade: Mapped[float | None] = mapped_column(Float, nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(32), nullable=True)
    material: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    dimensoes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    largura: Mapped[float | None] = mapped_column(Float, nullable=True)
    comprimento: Mapped[float | None] = mapped_column(Float, nullable=True)
    areaM2: Mapped[float | None] = mapped_column(Float, nullable=True)
    valorUnitario: Mapped[float | None] = mapped_column(Float, nullable=True)
    valorTotal: Mapped[float | None] = mapped_column(Float, nullable=True)
    precoPorM2: Mapped[float | None] = mapped_column(Float, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criadoEm: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orcamento: Mapped[Orcamento] = relationship(back_populates="itens")
