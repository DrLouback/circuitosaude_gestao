from src.db.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, Integer

class Atendimentos(Base):

    __tablename__ = "atendimentos"

    id: Mapped[int] =mapped_column(Integer, primary_key= True)
    index: Mapped[int] = mapped_column(Integer, name="index")
    Cliente: Mapped[str] = mapped_column(String, name="Cliente")
    Profissional: Mapped[str] = mapped_column(String, name="Profissional")
    Data_Hora: Mapped[DateTime] = mapped_column(DateTime, name="Data/Hora")
    Tipo_Atendimento: Mapped[str] = mapped_column(String, name="Tipo Atendimento")
    Status: Mapped[str] = mapped_column(String, name="Status")
    OBS: Mapped[str] = mapped_column(String, nullable=True, name="OBS")
    unidade: Mapped[str] = mapped_column(String, name="unidade")
    data: Mapped[DateTime] = mapped_column(DateTime, name="data")
    hora: Mapped[str] = mapped_column(String, name="hora")
    mes: Mapped[str] = mapped_column(String, name="mes")