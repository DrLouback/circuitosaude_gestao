from src.db.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, DECIMAL, Integer

class Stone(Base):
    __tablename__ = 'stone'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento: Mapped[str] = mapped_column(String)
    stonecode: Mapped[str] = mapped_column(String, unique= True)
    fantasia: Mapped[str] = mapped_column(String)
    categoria: Mapped[str] = mapped_column(String)
    data_venda: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    data_vencimento: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    vencimento_original: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    bandeira: Mapped[str] = mapped_column(String)
    produto: Mapped[str] = mapped_column(String)
    stone_id: Mapped[str] = mapped_column(String)
    qntd_parcelas: Mapped[int] = mapped_column(Integer)
    parcela: Mapped[int] = mapped_column(Integer)
    valor_bruto: Mapped[DECIMAL] = mapped_column(DECIMAL)
    valor_liquido: Mapped[DECIMAL] = mapped_column(DECIMAL)
    desconto: Mapped[DECIMAL] = mapped_column(DECIMAL)
    antecipacao: Mapped[DECIMAL] = mapped_column(DECIMAL)
    cartao: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    data_status: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    chave: Mapped[str] = mapped_column(String, nullable= True)
    unidade: Mapped[str] = mapped_column(String)
    mes_venda: Mapped[int] = mapped_column(Integer, nullable=True)
    mes_vencimento: Mapped[int] = mapped_column(Integer, nullable=True)