from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ClienteSchema(BaseModel):
    """Schema com os dados do cliente presentes no orcamento."""

    nome: Optional[str] = Field(
        default=None,
        description="Nome completo do cliente ou razao social encontrada no documento.",
    )
    documento: Optional[str] = Field(
        default=None,
        description="CPF, CNPJ ou outro identificador fiscal do cliente, se estiver presente.",
    )
    telefone: Optional[str] = Field(
        default=None,
        description="Telefone de contato do cliente exatamente como aparece no PDF.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Endereco de e-mail do cliente, se informado no documento.",
    )
    endereco: Optional[str] = Field(
        default=None,
        description="Endereco completo do cliente, preservando logradouro, numero e complemento.",
    )


class VendedorSchema(BaseModel):
    """Schema com os dados do vendedor ou responsavel comercial."""

    nome: Optional[str] = Field(
        default=None,
        description="Nome do vendedor, consultor ou responsavel comercial identificado no PDF.",
    )
    telefone: Optional[str] = Field(
        default=None,
        description="Telefone de contato do vendedor exatamente como aparece no documento.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Endereco de e-mail do vendedor, se estiver presente no PDF.",
    )
    empresa: Optional[str] = Field(
        default=None,
        description="Nome da empresa ou unidade comercial associada ao vendedor.",
    )


class ItemOrcamentoSchema(BaseModel):
    """Schema para cada item identificado no orcamento."""

    descricao: Optional[str] = Field(
        default=None,
        description="Descricao textual completa do item, sem resumir ou reescrever.",
    )
    quantidade: Optional[float] = Field(
        default=None,
        description="Quantidade numerica do item. Converta textos numericos para float quando aplicavel.",
    )
    unidade: Optional[str] = Field(
        default=None,
        description="Unidade de medida do item, como un, m, m2, kg, litro ou equivalente.",
    )
    material: Optional[str] = Field(
        default=None,
        description="Material principal do item, preservando a especificacao tecnica exata quando existir.",
    )
    dimensoes: Optional[str] = Field(
        default=None,
        description="Dimensoes, espessuras, bitolas ou medidas exatas do item, mantendo o texto tecnico original.",
    )
    valorUnitario: Optional[float] = Field(
        default=None,
        description="Valor unitario do item como numero float, removendo simbolos monetarios e separadores textuais.",
    )
    valorTotal: Optional[float] = Field(
        default=None,
        description="Valor total do item como numero float, removendo simbolos monetarios e separadores textuais.",
    )
    observacoes: Optional[str] = Field(
        default=None,
        description="Observacoes complementares relevantes do item, se houver.",
    )


class OrcamentoSchema(BaseModel):
    """Schema principal para a extracao estruturada de um orcamento em PDF."""

    numeroOrcamento: Optional[str] = Field(
        default=None,
        description="Numero, codigo ou identificador do orcamento encontrado no documento.",
    )
    dataEmissao: Optional[str] = Field(
        default=None,
        description="Data de emissao do orcamento no formato encontrado no PDF.",
    )
    validade: Optional[str] = Field(
        default=None,
        description="Prazo de validade do orcamento, se informado no documento.",
    )
    cliente: Optional[ClienteSchema] = Field(
        default=None,
        description="Bloco estruturado com os dados do cliente.",
    )
    vendedor: Optional[VendedorSchema] = Field(
        default=None,
        description="Bloco estruturado com os dados do vendedor ou representante comercial.",
    )
    itens: Optional[list[ItemOrcamentoSchema]] = Field(
        default=None,
        description="Lista de itens do orcamento, com descricoes, materiais, dimensoes e valores.",
    )
    subtotal: Optional[float] = Field(
        default=None,
        description="Valor subtotal do orcamento como numero float.",
    )
    desconto: Optional[float] = Field(
        default=None,
        description="Valor de desconto aplicado no orcamento como numero float, se existir.",
    )
    frete: Optional[float] = Field(
        default=None,
        description="Valor de frete como numero float, se estiver informado no documento.",
    )
    impostos: Optional[float] = Field(
        default=None,
        description="Valor de impostos ou tributos como numero float, se houver.",
    )
    valorTotal: Optional[float] = Field(
        default=None,
        description="Valor total final do orcamento como numero float.",
    )
    observacoesGerais: Optional[str] = Field(
        default=None,
        description="Observacoes gerais, condicoes comerciais ou notas adicionais do orcamento.",
    )
