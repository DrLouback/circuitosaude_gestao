from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type
from src.db.db import Base, engine, get_session
import pandas as pd

def input_db(df:pd.DataFrame, model: Type[Base]):

    Base.metadata.create_all(engine)
    with get_session() as session:

        for _, row in df.iterrows():
            try:
                row_dict = row.dropna().to_dict()
                obj = model(**row_dict)
    
                
                session.add(obj)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f'[Error] Erro ao inserir dados:  {e}')
        
         

               
               
