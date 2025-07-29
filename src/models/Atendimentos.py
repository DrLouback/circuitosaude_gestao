from src.db.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, Integer

class Atendimentos(Base):
    __tablename__ = 'atendimentos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    index: Mapped[int] = mapped_column(Integer)
    cliente: Mapped[str] = mapped_column(String)
    profissional: Mapped[str] = mapped_column(String)
    data_hora: Mapped[DateTime] = mapped_column(DateTime)
    atendimento: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    obs: Mapped[str] = mapped_column(String, nullable=True)
    data: Mapped[DateTime] = mapped_column(DateTime)
    unidade: Mapped[str] = mapped_column(String)
    id_atendimento: Mapped[str] = mapped_column(String, unique= True)
    