from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Atendimentos

async def get_agendamentos_experimentais(db: AsyncSession):
    stmt = select(Atendimentos).where(Atendimentos.Atendimentos.atendimento== "Pilates Experimental")
    result = await db.execute(stmt)
    return result.scalars().all()