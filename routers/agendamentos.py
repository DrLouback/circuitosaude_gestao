from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.async_database import get_db
from src.crud import get_agendamentos_experimentais
from src.schemas import AtendimentosResponse
from typing import List

router = APIRouter()

API_KEY = "seutokenseguro123"

@router.get("/agendamentos-experimentais", response_model=List[AtendimentosResponse.AtendimentoResponse])
async def listar_agendamentos(
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return await get_agendamentos_experimentais(db)