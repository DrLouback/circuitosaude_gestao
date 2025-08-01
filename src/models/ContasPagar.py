from src.db.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, DECIMAL, Integer

class ContasPagar(Base):
    __tablename__ = 'contas_pagar'
    id: Mapped[int] =mapped_column(Integer, primary_key= True)
    index: Mapped[int] = mapped_column(Integer)
    numero: Mapped[str] = mapped_column(String)
    fornecedor: Mapped[str] = mapped_column(String)
    titulo: Mapped[str] = mapped_column(String)
    centro_de_custo: Mapped[str] = mapped_column(String)
    forma: Mapped[str] = mapped_column(String)
    categoria: Mapped[str] = mapped_column(String)
    data_vencimento: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    data_pagamento: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    situacao: Mapped[str] = mapped_column(String)
    valor: Mapped[DECIMAL] = mapped_column(DECIMAL)
    unidade: Mapped[str] = mapped_column(String, nullable=True)
    mes_pagamento: Mapped[Integer] = mapped_column(Integer, nullable=True)
    id_conta_pagar: Mapped[str] = mapped_column(String, unique=True)