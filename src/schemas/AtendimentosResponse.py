from pydantic import BaseModel
from datetime import datetime

class AtendimentoResponse(BaseModel):
    id: int
    index: int
    cliente: str
    profissional: str
    data_hora: datetime
    atendimento: str
    status: str
    obs: str
    data: datetime
    unidade: str

    class Config:
        orm_mode = True
        