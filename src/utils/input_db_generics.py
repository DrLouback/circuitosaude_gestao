from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from typing import Type
from src.db.db import Base, engine, get_session
import pandas as pd

def input_db(df: pd.DataFrame, model: Type[Base], conflict_column: str = 'id'):
    """
    Insere ou atualiza registros de um DataFrame no banco usando UPSERT.
    
    Parameters:
    - df: DataFrame com os dados.
    - model: Classe ORM referente à tabela.
    - conflict_column: Coluna usada para detectar conflito (ex: 'numero').
    """
    Base.metadata.create_all(engine)
    
    with get_session() as session:
        for _, row in df.iterrows():
            try:
                row_dict = row.dropna().to_dict()

                stmt = insert(model).values(**row_dict)
                
                # remove a coluna de conflito do SET, senão o banco reclama
                update_dict = {k: v for k, v in row_dict.items() if k != conflict_column}

                stmt = stmt.on_conflict_do_update(
                    index_elements=[conflict_column],
                    set_=update_dict
                )
                
                session.execute(stmt)
                session.commit()

            except SQLAlchemyError as e:
                session.rollback()
                print(f'[Error] Erro ao inserir dados: {e}')