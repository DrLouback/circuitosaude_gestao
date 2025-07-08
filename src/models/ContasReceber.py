from src.db.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, DECIMAL, Integer


class ContasReceber(Base):
    __tablename__ = 'contas_receber'
    id: Mapped[int] = mapped_column(primary_key= True)
    index: Mapped[int] = mapped_column(Integer)
    numero: Mapped[int] = mapped_column(Integer, unique=True)
    cliente: Mapped[str] = mapped_column(String)
    cpf: Mapped[str] = mapped_column(String, nullable=True)
    centro_de_custo: Mapped[str] = mapped_column(String)
    forma: Mapped[str] = mapped_column(String)
    cod_transacao: Mapped[str] = mapped_column(String)
    data_vencimento: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    data_pagamento: Mapped[DateTime] = mapped_column(DateTime, nullable= True)
    data_recebimento: Mapped[DateTime] = mapped_column(DateTime, nullable= True)
    situacao: Mapped[str] = mapped_column(String)
    valor: Mapped[DECIMAL] = mapped_column(DECIMAL)
    unidade: Mapped[str] = mapped_column(String, nullable=True)
    mes_pagamento: Mapped[int] = mapped_column(Integer, nullable=True)
    mes_recebimento: Mapped[int] = mapped_column(Integer, nullable=True)
