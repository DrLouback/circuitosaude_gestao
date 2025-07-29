from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
# ----- Configurações -----
DB_ASYNC = os.getenv("DB_ASYNC")
print("DB_ASYNC:", DB_ASYNC)
engine = create_async_engine(DB_ASYNC, echo=False) # type: ignore
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ----- Lifespan -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔥 Iniciando aplicação e conectando ao banco de dados...")
    try:
        yield
    finally:
        await engine.dispose()

# Cria o app FastAPI e passa o lifespan
app = FastAPI(lifespan=lifespan)