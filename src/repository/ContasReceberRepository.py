from sqlalchemy.dialects.postgresql import insert  # troca para mysql se for MySQL
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from src.models.ContasReceber import ContasReceber  # ou ajuste para o caminho real do seu model

def upsert_contas_receber(df, engine):
    with Session(engine) as session:
        for _, row in df.iterrows():
            stmt = insert(ContasReceber).values(
                index=row['index'],
                numero=row['numero'],
                cliente=row['cliente'],
                cpf=row.get('cpf'),
                centro_de_custo=row.get('centro_de_custo'),
                forma=row.get('forma'),
                cod_transacao=row['cod_transacao'],
                data_vencimento=row.get('data_vencimento'),
                data_pagamento=row.get('data_pagamento'),
                data_recebimento=row.get('data_recebimento'),
                situacao=row['situacao'],
                valor=row.get('valor'),
                unidade=row.get('unidade'),
                mes_pagamento=row.get('mes_pagamento'),
                mes_recebimento=row.get('mes_recebimento'),
                telefone=row.get('telefone'),
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=['numero'],
                set_={
                    'index': stmt.excluded.index,
                    'cliente': stmt.excluded.cliente,
                    'cpf': stmt.excluded.cpf,
                    'centro_de_custo': stmt.excluded.centro_de_custo,
                    'forma': stmt.excluded.forma,
                    'cod_transacao': stmt.excluded.cod_transacao,
                    'data_vencimento': stmt.excluded.data_vencimento,
                    'data_pagamento': stmt.excluded.data_pagamento,
                    'data_recebimento': stmt.excluded.data_recebimento,
                    'situacao': stmt.excluded.situacao,
                    'valor': stmt.excluded.valor,
                    'unidade': stmt.excluded.unidade,
                    'mes_pagamento': stmt.excluded.mes_pagamento,
                    'mes_recebimento': stmt.excluded.mes_recebimento,
                    'telefone': stmt.excluded.telefone,
                }
            )

            session.execute(stmt)

        session.commit()